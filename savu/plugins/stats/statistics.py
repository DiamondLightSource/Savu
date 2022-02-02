"""
.. module:: statistics
   :platform: Unix
   :synopsis: Contains and processes statistics information for each plugin.

.. moduleauthor::Jacob Williamson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
from savu.plugins.stats.stats_utils import StatsUtils

import h5py as h5
import numpy as np
import os


class Statistics(object):
    _pattern_list = ["SINOGRAM", "PROJECTION", "TANGENTOGRAM", "VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D", "4D_SCAN", "SINOMOVIE"]
    no_stats_plugins = ["BasicOperations", "Mipmap"]
    _key_list = ["max", "min", "mean", "mean_std_dev", "median_std_dev", "RMSD"]


    def __init__(self):
        self.calc_stats = True
        self.stats = {'max': [], 'min': [], 'mean': [], 'std_dev': [], 'RSS': [], 'data_points': []}
        self.stats_before_processing = {'max': [], 'min': [], 'mean': [], 'std_dev': []}
        self.residuals = {'max': [], 'min': [], 'mean': [], 'std_dev': []}

    def setup(self, plugin_self):
        if plugin_self.name in Statistics.no_stats_plugins:
            self.calc_stats = False
        if self.calc_stats:
            self.plugin = plugin_self
            self.plugin_name = plugin_self.name
            self.pad_dims = []
            self._already_called = False
            self._set_pattern_info()
        if self.calc_stats:
            Statistics._any_stats = True


    @classmethod
    def _setup_class(cls, exp):
        """Sets up the statistics class for the whole plugin chain (only called once)"""
        cls._any_stats = False
        cls.count = 2
        cls.global_stats = {}
        cls.exp = exp
        n_plugins = len(exp.meta_data.plugin_list.plugin_list)
        for i in range(1, n_plugins + 1):
            cls.global_stats[i] = np.array([])
        cls.global_residuals = {}
        cls.plugin_numbers = {}
        cls.plugin_names = {}

        cls.path = exp.meta_data['out_path']
        if cls.path[-1] == '/':
            cls.path = cls.path[0:-1]
        cls.path = f"{cls.path}/stats"
        if not os.path.exists(cls.path):
            os.mkdir(cls.path)

    def set_slice_stats(self, slice, base_slice):
        slice_stats_before = self.calc_slice_stats(base_slice)
        slice_stats_after = self.calc_slice_stats(slice, base_slice)
        for key in list(self.stats_before_processing.keys()):
            self.stats_before_processing[key].append(slice_stats_before[key])
        for key in list(self.stats.keys()):
            self.stats[key].append(slice_stats_after[key])

    def calc_slice_stats(self, my_slice, base_slice=None):
        """Calculates and returns slice stats for the current slice.

        :param slice1: The slice whose stats are being calculated.
        """
        if my_slice is not None:
            slice_num = self.plugin.pcount
            my_slice = self._de_list(my_slice)
            my_slice = self._unpad_slice(my_slice)
            slice_stats = {'max': np.amax(my_slice).astype('float64'), 'min': np.amin(my_slice).astype('float64'),
                           'mean': np.mean(my_slice), 'std_dev': np.std(my_slice), 'data_points': my_slice.size}
            if base_slice is not None:
                base_slice = self._de_list(base_slice)
                base_slice = self._unpad_slice(base_slice)
                rss = self._calc_rss(my_slice, base_slice)
            else:
                rss = None
            slice_stats['RSS'] = rss
            return slice_stats
        return None

    def _calc_rss(self, array1, array2):  # residual sum of squares
        if array1.shape == array2.shape:
            residuals = np.subtract(array1, array2)
            rss = sum(value**2 for value in np.nditer(residuals))
        else:
            #print("Warning: cannot calculate RSS, arrays different sizes.")  # need to make this an actual warning
            rss = None
        return rss

    def _rmsd_from_rss(self, rss, n):
        return np.sqrt(rss/n)

    def calc_rmsd(self, array1, array2):
        if array1.shape == array2.shape:
            rss = self._calc_rss(array1, array2)
            rmsd = self._rmsd_from_rss(rss, array1.size)
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
        return volume_stats

    def set_volume_stats(self):
        """Calculates volume-wide statistics from slice stats, and updates class-wide arrays with these values.
        Links volume stats with the output dataset and writes slice stats to file.
        """
        p_num = Statistics.count
        name = self.plugin_name
        i = 2
        while name in list(Statistics.plugin_numbers.keys()):
            name = self.plugin_name + str(i)
            i += 1

        if len(self.stats['max']) != 0:
            stats_array = self.calc_volume_stats(self.stats)
            Statistics.global_residuals[p_num] = {}
            before_processing = self.calc_volume_stats(self.stats_before_processing)
            #for key in list(before_processing.keys()):
            #    Statistics.global_residuals[p_num][key] = Statistics.global_stats[p_num][key] - before_processing[key]
            if None not in self.stats['RSS']:
                total_rss = sum(self.stats['RSS'])
                n = sum(self.stats['data_points'])
                RMSD = self._rmsd_from_rss(total_rss, n)
                stats_array = np.append(stats_array, RMSD)
            #else:
            #    stats_array = np.append(stats_array[p_num], None)
            if len(Statistics.global_stats[p_num]) == 0:
                Statistics.global_stats[p_num] = stats_array
            else:
                Statistics.global_stats[p_num] = np.vstack([Statistics.global_stats[p_num], stats_array])
            Statistics.plugin_numbers[name] = p_num
            if p_num not in list(Statistics.plugin_names.keys()):
                Statistics.plugin_names[p_num] = name
            self._link_stats_to_datasets(Statistics.global_stats[Statistics.plugin_numbers[name]])

        slice_stats_array = np.array([self.stats['max'], self.stats['min'], self.stats['mean'], self.stats['std_dev']])
        self._write_stats_to_file3(p_num)
        self._already_called = True

    def get_stats(self, plugin_name, n=None, stat=None):
        """Returns stats associated with a certain plugin.

        :param plugin_name: name of the plugin whose associated stats are being fetched.
        :param n: In a case where there are multiple instances of **plugin_name** in the process list,
            specify the nth instance. Not specifying will select the first (or only) instance.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': }
        """
        name = plugin_name
        if n is not None and n not in (0, 1):
            name = name + str(n)
        p_num = Statistics.plugin_numbers[name]
        return self.get_stats_from_num(p_num, stat)

    def get_stats_from_num(self, p_num, stat=None, instance=0):
        """Returns stats associated with a certain plugin, given the plugin number (its place in the process list).

        :param p_num: Plugin  number of the plugin whose associated stats are being fetched.
            If p_num <= 0, it is relative to the plugin number of the current plugin being run.
            E.g current plugin number = 5, p_num = -2 --> will return stats of the third plugin.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': }
        """
        if p_num <= 0:
            p_num = Statistics.count + p_num
        if Statistics.global_stats[p_num].ndim == 1:
            stats_array = Statistics.global_stats[p_num]
        else:
            stats_array = Statistics.global_stats[p_num][instance]
        stats_dict = self._array_to_dict(stats_array)
        if stat is not None:
            return stats_dict[stat]
        else:
            return stats_dict

    def get_stats_from_dataset(self, dataset, stat=None, instance=None):
        """Returns stats associated with a dataset.

        :param dataset: The dataset whose associated stats are being fetched.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': }
        :param instance: In the (rare) case that there are multiple sets of stats associated with the dataset,
            specify which set to return.

        """
        key = "stats"
        stats = {}
        if instance is not None and instance not in (0, 1):
            key = key + str(instance)
        stats = dataset.meta_data.get(key)
        if stat is not None:
            return stats[stat]
        else:
            return stats

    def get_data_stats(self):
        return Statistics.data_stats

    def get_volume_stats(self):
        return Statistics.volume_stats

    def get_global_stats(self):
        return Statistics.global_stats

    def _array_to_dict(self, stats_array):
        stats_dict = {}
        for i, value in enumerate(stats_array):
            stats_dict[Statistics._key_list[i]] = value
        return stats_dict

    def _set_pattern_info(self):
        """Gathers information about the pattern of the data in the current plugin."""
        in_datasets, out_datasets = self.plugin.get_datasets()
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

    def _link_stats_to_datasets(self, stats):
        """Links the volume wide statistics to the output dataset(s)"""
        out_dataset = self.plugin.get_out_datasets()[0]
        n_datasets = self.plugin.nOutput_datasets()
        stats_dict = self._array_to_dict(stats)
        i = 2
        group_name = "stats"
        #out_dataset.data_info.set([group_name], stats)
        if n_datasets == 1:
            while group_name in list(out_dataset.meta_data.get_dictionary().keys()):
                group_name = f"stats{i}"
                i += 1
            for key in list(stats_dict.keys()):
                out_dataset.meta_data.set([group_name, key], stats_dict[key])

    def _write_stats_to_file2(self, p_num):
        path = Statistics.path
        filename = f"{path}/stats.h5"
        stats = Statistics.global_stats[p_num]
        array_dim = stats.shape
        self.hdf5 = Hdf5Utils(self.plugin.exp)
        group_name = f"{p_num}-{self.plugin_name}-stats"
        with h5.File(filename, "a") as h5file:
            if group_name not in h5file:
                group = h5file.create_group(group_name, track_order=None)
                dataset = self.hdf5.create_dataset_nofill(group, "stats", array_dim, stats.dtype)
                dataset[::] = stats[::]
            else:
                group = h5file[group_name]


    @classmethod
    def _write_stats_to_file4(cls):
        path = cls.path
        filename = f"{path}/stats.h5"
        stats = cls.global_stats
        cls.hdf5 = Hdf5Utils(cls.exp)
        for i in range(5):
            array = np.array([])
            stat = cls._key_list[i]
            for key in list(stats.keys()):
                if len(stats[key]) != 0:
                    if stats[key].ndim == 1:
                        array = np.append(array, stats[key][i])
                    else:
                        array = np.append(array, stats[key][0][i])
            array_dim = array.shape
            group_name = f"all-{stat}"
            with h5.File(filename, "a") as h5file:
                group = h5file.create_group(group_name, track_order=None)
                dataset = cls.hdf5.create_dataset_nofill(group, stat, array_dim, array.dtype)
                dataset[::] = array[::]

    def _write_stats_to_file3(self, p_num):
        path = Statistics.path
        filename = f"{path}/stats.h5"
        stats = self.global_stats
        self.hdf5 = Hdf5Utils(self.exp)
        with h5.File(filename, "a") as h5file:
            group = h5file.require_group("stats")
            if stats[p_num].shape != (0,):
                if str(p_num) in list(group.keys()):
                    del group[str(p_num)]
                dataset = group.create_dataset(str(p_num), shape=stats[p_num].shape, dtype=stats[p_num].dtype)
                dataset[::] = stats[p_num][::]
                dataset.attrs.create("plugin_name", self.plugin_names[p_num])
                dataset.attrs.create("pattern", self.pattern)


    def _write_stats_to_file(self, slice_stats_array, p_num):
        """Writes slice statistics to a h5 file"""
        path = Statistics.path
        filename = f"{path}/stats_p{p_num}_{self.plugin_name}.h5"
        slice_stats_dim = (slice_stats_array.shape[1],)
        self.hdf5 = Hdf5Utils(self.plugin.exp)
        with h5.File(filename, "a") as h5file:
            i = 2
            group_name = "/stats"
            while group_name in h5file:
                group_name = f"/stats{i}"
                i += 1
            group = h5file.create_group(group_name, track_order=None)
            max_ds = self.hdf5.create_dataset_nofill(group, "max", slice_stats_dim, slice_stats_array.dtype)
            min_ds = self.hdf5.create_dataset_nofill(group, "min", slice_stats_dim, slice_stats_array.dtype)
            mean_ds = self.hdf5.create_dataset_nofill(group, "mean", slice_stats_dim, slice_stats_array.dtype)
            std_dev_ds = self.hdf5.create_dataset_nofill(group, "standard_deviation",
                                                         slice_stats_dim, slice_stats_array.dtype)
            if slice_stats_array.shape[0] == 5:
                rmsd_ds = self.hdf5.create_dataset_nofill(group, "RMSD", slice_stats_dim, slice_stats_array.dtype)
                rmsd_ds[::] = slice_stats_array[4]
            max_ds[::] = slice_stats_array[0]
            min_ds[::] = slice_stats_array[1]
            mean_ds[::] = slice_stats_array[2]
            std_dev_ds[::] = slice_stats_array[3]

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
            self.slice_list, self.pad = self._get_unpadded_slice_list(slice1, slice_dims)
        if self.pad:
            #for slice_dim in slice_dims:
            slice_dim = slice_dims[0]
            temp_slice = np.swapaxes(slice1, 0, slice_dim)
            temp_slice = temp_slice[self.slice_list[slice_dim]]
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
        if cls._any_stats:
            stats_utils = StatsUtils()
            stats_utils.generate_figures(f"{cls.path}/stats.h5", cls.path)
