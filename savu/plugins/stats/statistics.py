"""
.. module:: statistics
   :platform: Unix
   :synopsis: Contains and processes statistics information for each plugin.

.. moduleauthor::Jacob Williamson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
from savu.plugins.stats.stats_utils import StatsUtils
from savu.core.iterate_plugin_group_utils import check_if_in_iterative_loop

import h5py as h5
import numpy as np
import os
from mpi4py import MPI


class Statistics(object):
    _pattern_list = ["SINOGRAM", "PROJECTION", "TANGENTOGRAM", "VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D", "4D_SCAN", "SINOMOVIE"]
    _no_stats_plugins = ["BasicOperations", "Mipmap"]
    _key_list = ["max", "min", "mean", "mean_std_dev", "median_std_dev", "NRMSD"]


    def __init__(self):
        self.calc_stats = True
        self.stats = {'max': [], 'min': [], 'mean': [], 'std_dev': [], 'RSS': [], 'data_points': []}
        self.stats_before_processing = {'max': [], 'min': [], 'mean': [], 'std_dev': []}
        self.residuals = {'max': [], 'min': [], 'mean': [], 'std_dev': []}
        self._repeat_count = 0
        self.p_num = None

    def setup(self, plugin_self, pattern=None):
        if plugin_self.name in Statistics._no_stats_plugins:
            self.calc_stats = False
        if self.calc_stats:
            self.plugin = plugin_self
            self.plugin_name = plugin_self.name
            self._pad_dims = []
            self._already_called = False
            if pattern:
                self.pattern = pattern
            else:
                self._set_pattern_info()
        if self.calc_stats:
            Statistics._any_stats = True
        self._setup_iterative()

    def _setup_iterative(self):
        self._iterative_group = check_if_in_iterative_loop(Statistics.exp)
        if self._iterative_group:
            if self._iterative_group.start_index == Statistics.count:
                Statistics._loop_counter += 1
                Statistics.loop_stats.append({"NRMSD": np.array([])})
            self.l_num = Statistics._loop_counter - 1

    @classmethod
    def _setup_class(cls, exp):
        """Sets up the statistics class for the whole plugin chain (only called once)"""
        if exp.meta_data.get("stats") == "on":
            cls.stats_flag = True
        elif exp.meta_data.get("stats") == "off":
            cls.stats_flag = False
        cls._any_stats = False
        cls.count = 2
        cls.global_stats = {}
        cls.loop_stats = []
        cls.exp = exp
        cls.n_plugins = len(exp.meta_data.plugin_list.plugin_list)
        for i in range(1, cls.n_plugins + 1):
            cls.global_stats[i] = np.array([])
        cls.global_residuals = {}
        cls.plugin_numbers = {}
        cls.plugin_names = {}
        cls._loop_counter = 0
        cls.path = exp.meta_data['out_path']
        if cls.path[-1] == '/':
            cls.path = cls.path[0:-1]
        cls.path = f"{cls.path}/stats"
        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(cls.path):
                os.mkdir(cls.path)

    def set_slice_stats(self, slice, base_slice=None, pad=True):
        slice_stats_after = self.calc_slice_stats(slice, base_slice, pad=pad)
        if base_slice:
            slice_stats_before = self.calc_slice_stats(base_slice, pad=pad)
            for key in list(self.stats_before_processing.keys()):
                self.stats_before_processing[key].append(slice_stats_before[key])
        for key in list(self.stats.keys()):
            self.stats[key].append(slice_stats_after[key])

    def calc_slice_stats(self, my_slice, base_slice=None, pad=True):
        """Calculates and returns slice stats for the current slice.

        :param slice1: The slice whose stats are being calculated.
        """
        if my_slice is not None:
            my_slice = self._de_list(my_slice)
            if pad:
                my_slice = self._unpad_slice(my_slice)
            slice_stats = {'max': np.amax(my_slice).astype('float64'), 'min': np.amin(my_slice).astype('float64'),
                           'mean': np.mean(my_slice), 'std_dev': np.std(my_slice), 'data_points': my_slice.size}
            if base_slice is not None:
                base_slice = self._de_list(base_slice)
                base_slice = self._unpad_slice(base_slice)
                rss = self.calc_rss(my_slice, base_slice)
            else:
                rss = None
            slice_stats['RSS'] = rss
            return slice_stats
        return None

    def calc_rss(self, array1, array2):  # residual sum of squares
        if array1.shape == array2.shape:
            residuals = np.subtract(array1, array2)
            rss = sum(value**2 for value in np.nditer(residuals))
        else:
            #print("Warning: cannot calculate RSS, arrays different sizes.")
            rss = None
        return rss

    def rmsd_from_rss(self, rss, n):
        return np.sqrt(rss/n)

    def calc_rmsd(self, array1, array2):
        if array1.shape == array2.shape:
            rss = self.calc_rss(array1, array2)
            rmsd = self.rmsd_from_rss(rss, array1.size)
        else:
            print("Warning: cannot calculate RMSD, arrays different sizes.")  # need to make this an actual warning
            rmsd = None
        return rmsd

    def calc_stats_residuals(self, stats_before, stats_after):
        residuals = {'max': None, 'min': None, 'mean': None, 'std_dev': None}
        for key in list(residuals.keys()):
            residuals[key] = stats_after[key] - stats_before[key]
        return residuals

    def set_stats_residuals(self, residuals):
        self.residuals['max'].append(residuals['max'])
        self.residuals['min'].append(residuals['min'])
        self.residuals['mean'].append(residuals['mean'])
        self.residuals['std_dev'].append(residuals['std_dev'])

    def calc_volume_stats(self, slice_stats):
        volume_stats = np.array([max(slice_stats['max']), min(slice_stats['min']), np.mean(slice_stats['mean']),
                                np.mean(slice_stats['std_dev']), np.median(slice_stats['std_dev'])])
        if None not in slice_stats['RSS']:
            total_rss = sum(slice_stats['RSS'])
            n = sum(slice_stats['data_points'])
            RMSD = self.rmsd_from_rss(total_rss, n)
            the_range = volume_stats[0] - volume_stats[1]
            NRMSD = RMSD / the_range  # normalised RMSD (dividing by the range)
            volume_stats = np.append(volume_stats, NRMSD)
        else:
            #volume_stats = np.append(volume_stats, None)
            pass
        return volume_stats

    def _set_loop_stats(self):
        # NEED TO CHANGE THIS - MUST USE SLICES
        data_obj1 = list(self._iterative_group._ip_data_dict["iterating"].keys())[0]
        data_obj2 = self._iterative_group._ip_data_dict["iterating"][data_obj1]
        RMSD = self.calc_rmsd(data_obj1.data, data_obj2.data)
        the_range = self.get_stats(self.p_num, stat="max", instance=self._iterative_group._ip_iteration) -\
                self.get_stats(self.p_num, stat="min", instance=self._iterative_group._ip_iteration)
        NRMSD = RMSD/the_range
        Statistics.loop_stats[self.l_num]["NRMSD"] = np.append(Statistics.loop_stats[self.l_num]["NRMSD"], NRMSD)

    def set_volume_stats(self):
        """Calculates volume-wide statistics from slice stats, and updates class-wide arrays with these values.
        Links volume stats with the output dataset and writes slice stats to file.
        """
        stats = self.stats
        combined_stats = self._combine_mpi_stats(stats)
        if not self.p_num:
            self.p_num = Statistics.count
        p_num = self.p_num
        name = self.plugin_name
        i = 2
        if not self._iterative_group:
            while name in list(Statistics.plugin_numbers.keys()):
                name = self.plugin_name + str(i)
                i += 1
        elif self._iterative_group._ip_iteration == 0:
            while name in list(Statistics.plugin_numbers.keys()):
                name = self.plugin_name + str(i)
                i += 1

        if p_num not in list(Statistics.plugin_names.keys()):
            Statistics.plugin_names[p_num] = name
        Statistics.plugin_numbers[name] = p_num
        if len(self.stats['max']) != 0:
            stats_array = self.calc_volume_stats(combined_stats)
            Statistics.global_residuals[p_num] = {}
            #before_processing = self.calc_volume_stats(self.stats_before_processing)
            #for key in list(before_processing.keys()):
            #    Statistics.global_residuals[p_num][key] = Statistics.global_stats[p_num][key] - before_processing[key]

            if len(Statistics.global_stats[p_num]) == 0:
                Statistics.global_stats[p_num] = stats_array
            else:
                Statistics.global_stats[p_num] = np.vstack([Statistics.global_stats[p_num], stats_array])

            stats_dict = self._array_to_dict(stats_array)
            self._link_stats_to_datasets(stats_dict)

        if self._iterative_group:
            if self._iterative_group.end_index == p_num and self._iterative_group._ip_iteration != 0:
                self._set_loop_stats()

        self._write_stats_to_file(p_num)
        self._already_called = True
        self._repeat_count += 1

    def get_stats(self, p_num, stat=None, instance=-1):
        """Returns stats associated with a certain plugin, given the plugin number (its place in the process list).

        :param p_num: Plugin  number of the plugin whose associated stats are being fetched.
            If p_num <= 0, it is relative to the plugin number of the current plugin being run.
            E.g current plugin number = 5, p_num = -2 --> will return stats of the third plugin.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': , 'NRMSD' }
        :param instance: In cases where there are multiple set of stats associated with a plugin
            due to loops or multi-parameters, specify which set you want to retrieve, i.e 3 to retrieve the
            stats associated with the third run of a plugin. Pass 'all' to get a list of all sets.
        """
        if p_num <= 0:
            try:
                p_num = self.p_num + p_num
            except TypeError:
                p_num = Statistics.count + p_num
        if Statistics.global_stats[p_num].ndim == 1 and instance in (None, 0, 1, -1, "all"):
            stats_array = Statistics.global_stats[p_num]
        else:
            if instance == "all":
                stats_list = [self.get_stats(p_num, stat=stat, instance=1)]
                n = 2
                if Statistics.global_stats[p_num].ndim != 1:
                    while n <= len(Statistics.global_stats[p_num]):
                        stats_list.append(self.get_stats(p_num, stat=stat, instance=n))
                        n += 1
                return stats_list
            if instance > 0:
                instance -= 1
            stats_array = Statistics.global_stats[p_num][instance]
        stats_dict = self._array_to_dict(stats_array)
        if stat is not None:
            return stats_dict[stat]
        else:
            return stats_dict

    def get_stats_from_name(self, plugin_name, n=None, stat=None, instance=-1):
        """Returns stats associated with a certain plugin.

        :param plugin_name: name of the plugin whose associated stats are being fetched.
        :param n: In a case where there are multiple instances of **plugin_name** in the process list,
            specify the nth instance. Not specifying will select the first (or only) instance.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': , 'NRMSD' }
        :param instance: In cases where there are multiple set of stats associated with a plugin
            due to loops or multi-parameters, specify which set you want to retrieve, i.e 3 to retrieve the
            stats associated with the third run of a plugin. Pass 'all' to get a list of all sets.
        """
        name = plugin_name
        if n in (None, 0, 1):
            name = name + str(n)
        p_num = Statistics.plugin_numbers[name]
        return self.get_stats(p_num, stat, instance)

    def get_stats_from_dataset(self, dataset, stat=None, instance=-1):
        """Returns stats associated with a dataset.

        :param dataset: The dataset whose associated stats are being fetched.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': , 'NRMSD'}
        :param instance: In cases where there are multiple set of stats associated with a dataset
            due to loops or multi-parameters, specify which set you want to retrieve, i.e 3 to retrieve the
            stats associated with the third run of a plugin. Pass 'all' to get a list of all sets.

        """
        key = "stats"
        stats = {}

        stats_list = [dataset.meta_data.get("stats")]
        n = 2
        while ("stats" + str(n)) in list(dataset.meta_data.get_dictionary().keys()):
            stats_list.append(dataset.meta_data.get("stats" + str(n)))
            n += 1
        if stat:
            for i in range(len(stats_list)):
                stats_list[i] = stats_list[i][stat]
        if instance in (None, 0, 1):
            stats = stats_list[0]
        elif instance == "all":
            stats = stats_list
        else:
            if instance >= 2:
                instance -= 1
            stats = stats_list[instance]
        return stats

    def _combine_mpi_stats(self, slice_stats):
        comm = MPI.COMM_WORLD
        combined_stats_list = comm.allgather(slice_stats)
        combined_stats = {'max': [], 'min': [], 'mean': [], 'std_dev': [], 'RSS': [], 'data_points': []}
        for single_stats in combined_stats_list:
            for key in list(single_stats.keys()):
                combined_stats[key] += single_stats[key]
        return combined_stats

    def _array_to_dict(self, stats_array):
        stats_dict = {}
        for i, value in enumerate(stats_array):
            stats_dict[Statistics._key_list[i]] = value
        return stats_dict

    def _set_pattern_info(self):
        """Gathers information about the pattern of the data in the current plugin."""
        out_datasets = self.plugin.get_out_datasets()
        try:
            self.pattern = self.plugin.parameters['pattern']
            if self.pattern == None:
                raise KeyError
        except KeyError:
            if not out_datasets:
                self.pattern = None
            else:
                patterns = out_datasets[0].get_data_patterns()
                for pattern in patterns:
                    if 1 in patterns.get(pattern)["slice_dims"]:
                        self.pattern = pattern
                        break
        self.calc_stats = False
        for dataset in out_datasets:
            if bool(set(Statistics._pattern_list) & set(dataset.data_info.get("data_patterns"))):
                self.calc_stats = True

    def _link_stats_to_datasets(self, stats_dict):
        """Links the volume wide statistics to the output dataset(s)"""
        out_dataset = self.plugin.get_out_datasets()[0]
        n_datasets = self.plugin.nOutput_datasets()

        i = 2
        group_name = "stats"
        #out_dataset.data_info.set([group_name], stats)
        while group_name in list(out_dataset.meta_data.get_dictionary().keys()):
            group_name = f"stats{i}"
            i += 1
        for key in list(stats_dict.keys()):
            out_dataset.meta_data.set([group_name, key], stats_dict[key])

    def _write_stats_to_file(self, p_num=None, plugin_name=None):
        if p_num is None:
            p_num = self.p_num
        if plugin_name is None:
            plugin_name = self.plugin_names[p_num]
        path = Statistics.path
        filename = f"{path}/stats.h5"
        stats = self.global_stats[p_num]
        self.hdf5 = Hdf5Utils(self.exp)
        with h5.File(filename, "a", driver="mpio", comm=MPI.COMM_WORLD) as h5file:
            group = h5file.require_group("stats")
            if stats.shape != (0,):
                if str(p_num) in list(group.keys()):
                    del group[str(p_num)]
                dataset = group.create_dataset(str(p_num), shape=stats.shape, dtype=stats.dtype)
                dataset[::] = stats[::]
                dataset.attrs.create("plugin_name", plugin_name)
                dataset.attrs.create("pattern", self.pattern)
            if self._iterative_group:
                l_stats = Statistics.loop_stats[self.l_num]
                group1 = h5file.require_group("iterative")
                if self._iterative_group._ip_iteration == self._iterative_group._ip_fixed_iterations - 1\
                        and self.p_num == self._iterative_group.end_index:
                    dataset1 = group1.create_dataset(str(self.l_num), shape=l_stats["NRMSD"].shape, dtype=l_stats["NRMSD"].dtype)
                    dataset1[::] = l_stats["NRMSD"][::]
                    loop_plugins = []
                    for i in range(self._iterative_group.start_index, self._iterative_group.end_index + 1):
                        loop_plugins.append(self.plugin_names[i])
                    dataset1.attrs.create("loop_plugins", loop_plugins)
                    dataset.attrs.create("n_loop_plugins", len(loop_plugins))

    def write_slice_stats_to_file(self, slice_stats=None, p_num=None):
        """Writes slice statistics to a h5 file. Placed in the stats folder in the output directory."""
        if not slice_stats:
            slice_stats = self.stats
        if not p_num:
            p_num = self.count
            plugin_name = self.plugin_name
        else:
            plugin_name = self.plugin_names[p_num]
        combined_stats = self._combine_mpi_stats(slice_stats)
        slice_stats_arrays = {}
        datasets = {}
        path = Statistics.path
        filename = f"{path}/stats_p{p_num}_{plugin_name}.h5"
        self.hdf5 = Hdf5Utils(self.plugin.exp)
        with h5.File(filename, "a", driver="mpio", comm=MPI.COMM_WORLD) as h5file:
            i = 2
            group_name = "/stats"
            while group_name in h5file:
                group_name = f"/stats{i}"
                i += 1
            group = h5file.create_group(group_name, track_order=None)
            for key in list(combined_stats.keys()):
                slice_stats_arrays[key] = np.array(combined_stats[key])
                datasets[key] = self.hdf5.create_dataset_nofill(group, key, (len(slice_stats_arrays[key]),), slice_stats_arrays[key].dtype)
                datasets[key][::] = slice_stats_arrays[key]

    def _unpad_slice(self, slice1):
        """If data is padded in the slice dimension, removes this pad."""
        out_datasets = self.plugin.get_out_datasets()
        if len(out_datasets) == 1:
            out_dataset = out_datasets[0]
        else:
            for dataset in out_datasets:
                if self.pattern in list(dataset.data_info.get(["data_patterns"]).keys()):
                    out_dataset = dataset
                    break
        slice_dims = out_dataset.get_slice_dimensions()
        if self.plugin.pcount == 0:
            self._slice_list, self._pad = self._get_unpadded_slice_list(slice1, slice_dims)
        if self._pad:
            #for slice_dim in slice_dims:
            slice_dim = slice_dims[0]
            temp_slice = np.swapaxes(slice1, 0, slice_dim)
            temp_slice = temp_slice[self._slice_list[slice_dim]]
            slice1 = np.swapaxes(temp_slice, 0, slice_dim)
        return slice1

    def _get_unpadded_slice_list(self, slice1, slice_dims):
        """Creates slice object(s) to un-pad slices in the slice dimension(s)."""
        slice_list = list(self.plugin.slice_list[0])
        pad = False
        if len(slice_list) == len(slice1.shape):
            #for i in slice_dims:
            i = slice_dims[0]
            slice_width = self.plugin.slice_list[0][i].stop - self.plugin.slice_list[0][i].start
            if slice_width != slice1.shape[i]:
                pad = True
                pad_width = (slice1.shape[i] - slice_width) // 2  # Assuming symmetrical padding
                slice_list[i] = slice(pad_width, pad_width + 1, 1)
            return tuple(slice_list), pad
        else:
            return self.plugin.slice_list[0], pad

    def _de_list(self, slice1):
        """If the slice is in a list, remove it from that list."""
        if type(slice1) == list:
            if len(slice1) != 0:
                slice1 = slice1[0]
                slice1 = self._de_list(slice1)
        return slice1


    @classmethod
    def _count(cls):
        cls.count += 1

    @classmethod
    def _post_chain(cls):
        if cls._any_stats & cls.stats_flag:
            stats_utils = StatsUtils()
            stats_utils.generate_figures(f"{cls.path}/stats.h5", cls.path)
