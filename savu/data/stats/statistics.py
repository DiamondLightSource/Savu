"""
.. module:: statistics
   :platform: Unix
   :synopsis: Contains and processes statistics information for each plugin.

.. moduleauthor::Jacob Williamson <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
from savu.data.stats.stats_utils import StatsUtils
from savu.core.iterate_plugin_group_utils import check_if_in_iterative_loop
import savu.core.utils as cu

import time
import h5py as h5
import numpy as np
import os
from mpi4py import MPI
from collections import OrderedDict

class Statistics(object):
    _pattern_list = ["SINOGRAM", "PROJECTION", "TANGENTOGRAM", "VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D", "4D_SCAN", "SINOMOVIE"]
    _no_stats_plugins = ["BasicOperations", "Mipmap", "UnetApply"]
    _possible_stats = ("max", "min", "mean", "mean_std_dev", "median_std_dev", "NRMSD", "zeros", "zeros%", "range_used")  # list of possible stats
    _volume_to_slice = {"max": "max", "min": "min", "mean": "mean", "mean_std_dev": "std_dev",
                        "median_std_dev": "std_dev", "NRMSD": ("RSS", "data_points", "max", "min"),
                        "zeros": ("zeros", "data_points"), "zeros%": ("zeros", "data_points"),
                        "range_used": ("min", "max")}  # volume stat: required slice stat(s)
    #_savers = ["Hdf5Saver", "ImageSaver", "MrcSaver", "TiffSaver", "XrfSaver"]
    _has_setup = False


    def __init__(self):

        self.calc_stats = True
        self.stats_before_processing = {'max': [], 'min': [], 'mean': [], 'std_dev': []}
        self.residuals = {'max': [], 'min': [], 'mean': [], 'std_dev': []}
        self._repeat_count = 0
        self.plugin = None
        self.p_num = None
        self.stats_key = ["max", "min", "mean", "mean_std_dev", "median_std_dev", "RMSD"]
        self.slice_stats_key = None
        self.stats = None
        self.GPU = False
        self._iterative_group = None

    def setup(self, plugin_self, pattern=None):
        if not Statistics._has_setup:
            self._setup_class(plugin_self.exp)
        self.plugin_name = plugin_self.name
        self.p_num = Statistics.count
        self.plugin = plugin_self
        self.set_stats_key(self.stats_key)
        self.stats = {stat: [] for stat in self.slice_stats_key}
        if plugin_self.name in Statistics._no_stats_plugins:
            self.calc_stats = False
        if self.calc_stats:
            self._pad_dims = []
            self._already_called = False
            if pattern is not None:
                self.pattern = pattern
            else:
                self._set_pattern_info()
        if self.calc_stats:
            Statistics._any_stats = True
        self._setup_4d()
        self._setup_iterative()

    def _setup_iterative(self):
        self._iterative_group = check_if_in_iterative_loop(Statistics.exp)
        if self._iterative_group:
            if self._iterative_group.start_index == Statistics.count:
                Statistics._loop_counter += 1
                Statistics.loop_stats.append({"NRMSD": np.array([])})
            self.l_num = Statistics._loop_counter - 1

    def _setup_4d(self):
        in_dataset, out_dataset = self.plugin.get_datasets()
        if in_dataset[0].data_info["nDims"] == 4:
            self._4d = True
            shape = out_dataset[0].data_info["shape"]
            self._volume_total_points = shape[0] * shape[1] * shape[2]
        else:
            self._4d = False

    @classmethod
    def _setup_class(cls, exp):
        """Sets up the statistics class for the whole plugin chain (only called once)"""
        if exp.meta_data.get("stats") == "on":
            cls._stats_flag = True
        elif exp.meta_data.get("stats") == "off":
            cls._stats_flag = False
        cls._any_stats = False
        cls.exp = exp
        cls.count = 2
        cls.global_stats = {}
        cls.global_times = {}
        cls.loop_stats = []
        cls.n_plugins = len(exp.meta_data.plugin_list.plugin_list)
        for i in range(1, cls.n_plugins + 1):
            cls.global_stats[i] = {}
            cls.global_times[i] = 0
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
        cls._has_setup = True

    def get_stats(self, p_num=None, stat=None, instance=-1):
        """Returns stats associated with a certain plugin, given the plugin number (its place in the process list).

        :param p_num: Plugin  number of the plugin whose associated stats are being fetched.
            If p_num <= 0, it is relative to the plugin number of the current plugin being run.
            E.g current plugin number = 5, p_num = -2 --> will return stats of the third plugin.
            By default will gather stats for the current plugin.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': , 'NRMSD': }
        :param instance: In cases where there are multiple set of stats associated with a plugin
            due to iterative loops or multi-parameters, specify which set you want to retrieve, i.e 3 to retrieve the
            stats associated with the third run of a plugin. Pass 'all' to get a list of all sets.
            By default will retrieve the most recent set.
        """
        if p_num is None:
            p_num = self.p_num
        if p_num <= 0:
            try:
                p_num = self.p_num + p_num
            except TypeError:
                p_num = Statistics.count + p_num
        if instance == "all":
            stats_list = [self.get_stats(p_num, stat=stat, instance=1)]
            n = 2
            while n <= len(Statistics.global_stats[p_num]):
                stats_list.append(self.get_stats(p_num, stat=stat, instance=n))
                n += 1
            return stats_list
        if instance > 0:
            instance -= 1
        stats_dict = Statistics.global_stats[p_num][instance]
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
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': , 'NRMSD': }
        :param instance: In cases where there are multiple set of stats associated with a plugin
            due to iterative loops or multi-parameters, specify which set you want to retrieve, i.e 3 to retrieve the
            stats associated with the third run of a plugin. Pass 'all' to get a list of all sets.
            By default will retrieve the most recent set.
        """
        name = plugin_name
        if n not in (None, 0, 1):
            name = name + str(n)
        p_num = Statistics.plugin_numbers[name]
        return self.get_stats(p_num, stat, instance)

    def get_stats_from_dataset(self, dataset, stat=None, instance=-1):
        """Returns stats associated with a dataset.

        :param dataset: The dataset whose associated stats are being fetched.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': , 'NRMSD': }
        :param instance: In cases where there are multiple set of stats associated with a dataset
            due to iterative loops or multi-parameters, specify which set you want to retrieve, i.e 3 to retrieve the
            stats associated with the third run of a plugin. Pass 'all' to get a list of all sets.
            By default will retrieve the most recent set.
        """
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

    def set_stats_key(self, stats_key):
        """Changes which stats are to be calculated for the current plugin.

        :param stats_key: List of stats to be calculated.
        """
        valid = Statistics._possible_stats
        stats_key = sorted(set(valid).intersection(stats_key), key=lambda stat: valid.index(stat))
        self.stats_key = stats_key
        self.slice_stats_key = list(set(self._flatten(list(Statistics._volume_to_slice[stat] for stat in stats_key))))
        if "data_points" not in self.slice_stats_key:
            self.slice_stats_key.append("data_points")  # Data points is essential

    def set_slice_stats(self, my_slice, base_slice=None, pad=True):
        """Sets slice stats for the current slice.

        :param my_slice: The slice whose stats are being set.
        :param base_slice: Provide a base slice to calculate residuals from, to calculate RMSD.
        :param pad: Specify whether slice is padded or not (usually can leave as True even if slice is not padded).
        """
        if 0 not in my_slice.shape:
            try:
                slice_stats = self.calc_slice_stats(my_slice, base_slice=base_slice, pad=pad)
            except:
                pass
            if slice_stats is not None:
                for key, value in slice_stats.items():
                    self.stats[key].append(value)
                if self._4d:
                    if sum(self.stats["data_points"]) >= self._volume_total_points:
                        self.set_volume_stats()
            else:
                self.calc_stats = False
        else:
            self.calc_stats = False

    def calc_slice_stats(self, my_slice, base_slice=None, pad=True):
        """Calculates and returns slice stats for the current slice.

        :param my_slice: The slice whose stats are being calculated.
        :param base_slice: Provide a base slice to calculate residuals from, to calculate RMSD.
        :param pad: Specify whether slice is padded or not (usually can leave as True even if slice is not padded).
        """
        if my_slice is not None:
            my_slice = self._de_list(my_slice)
            if pad:
                my_slice = self._unpad_slice(my_slice)
            slice_stats = {}
            if "max" in self.slice_stats_key:
                slice_stats["max"] = np.amax(my_slice).astype('float64')
            if "min" in self.slice_stats_key:
                slice_stats["min"] = np.amin(my_slice).astype('float64')
            if "mean" in self.slice_stats_key:
                slice_stats["mean"] = np.mean(my_slice)
            if "std_dev" in self.slice_stats_key:
                slice_stats["std_dev"] = np.std(my_slice)
            if "zeros" in self.slice_stats_key:
                slice_stats["zeros"] = self.calc_zeros(my_slice)
            if "data_points" in self.slice_stats_key:
                slice_stats["data_points"] = my_slice.size
            if "RSS" in self.slice_stats_key and base_slice is not None:
                base_slice = self._de_list(base_slice)
                base_slice = self._unpad_slice(base_slice)
                slice_stats["RSS"] = self.calc_rss(my_slice, base_slice)
            if "dtype" not in self.stats:
                self.stats["dtype"] = my_slice.dtype
            return slice_stats
        return None

    @staticmethod
    def calc_zeros(my_slice):
        return my_slice.size - np.count_nonzero(my_slice)

    @staticmethod
    def calc_rss(array1, array2):  # residual sum of squares # Need to benchmark
        if array1.shape == array2.shape:
            residuals = np.subtract(array1, array2)
            rss = np.sum(residuals.flatten() ** 2)
        else:
            logging.debug("Cannot calculate RSS, arrays different sizes.")
            rss = None
        return rss

    @staticmethod
    def rmsd_from_rss(rss, n):
        return np.sqrt(rss/n)

    def calc_rmsd(self, array1, array2):
        if array1.shape == array2.shape:
            rss = self.calc_rss(array1, array2)
            rmsd = self.rmsd_from_rss(rss, array1.size)
        else:
            logging.error("Cannot calculate RMSD, arrays different sizes.")
            rmsd = None
        return rmsd

    def calc_stats_residuals(self, stats_before, stats_after):  # unused
        residuals = {'max': None, 'min': None, 'mean': None, 'std_dev': None}
        for key in list(residuals.keys()):
            residuals[key] = stats_after[key] - stats_before[key]
        return residuals

    def set_stats_residuals(self, residuals):  #unused
        self.residuals['max'].append(residuals['max'])
        self.residuals['min'].append(residuals['min'])
        self.residuals['mean'].append(residuals['mean'])
        self.residuals['std_dev'].append(residuals['std_dev'])

    def calc_volume_stats(self, slice_stats):
        """Calculates and returns volume-wide stats from slice-wide stats.

        :param slice_stats: The slice-wide stats that the volume-wide stats are calculated from.
        """
        slice_stats = slice_stats
        volume_stats = {}
        if "max" in self.stats_key:
            volume_stats["max"] = max(slice_stats["max"])
        if "min" in self.stats_key:
            volume_stats["min"] = min(slice_stats["min"])
        if "mean" in self.stats_key:
            volume_stats["mean"] = np.mean(slice_stats["mean"])
        if "mean_std_dev" in self.stats_key:
            volume_stats["mean_std_dev"] = np.mean(slice_stats["std_dev"])
        if "median_std_dev" in self.stats_key:
            volume_stats["median_std_dev"] = np.median(slice_stats["std_dev"])
        if "NRMSD" in self.stats_key and None not in slice_stats["RSS"]:
            total_rss = sum(slice_stats["RSS"])
            n = sum(slice_stats["data_points"])
            RMSD = self.rmsd_from_rss(total_rss, n)
            the_range = volume_stats["max"] - volume_stats["min"]
            NRMSD = RMSD / the_range  # normalised RMSD (dividing by the range)
            volume_stats["NRMSD"] = NRMSD
        if "zeros" in self.stats_key:
            volume_stats["zeros"] = sum(slice_stats["zeros"])
        if "zeros%" in self.stats_key:
            volume_stats["zeros%"] = (volume_stats["zeros"] / sum(slice_stats["data_points"])) * 100
        if "range_used" in self.stats_key:
            my_range = volume_stats["max"] - volume_stats["min"]
            if "int" in str(self.stats["dtype"]):
                possible_max = np.iinfo(self.stats["dtype"]).max
                possible_min = np.iinfo(self.stats["dtype"]).min
                self.stats["possible_max"] = possible_max
                self.stats["possible_min"] = possible_min
            elif "float" in str(self.stats["dtype"]):
                possible_max = np.finfo(self.stats["dtype"]).max
                possible_min = np.finfo(self.stats["dtype"]).min
                self.stats["possible_max"] = possible_max
                self.stats["possible_min"] = possible_min
            possible_range = possible_max - possible_min
            volume_stats["range_used"] = (my_range / possible_range) * 100
        return volume_stats

    def _set_loop_stats(self):
        # NEED TO CHANGE THIS - MUST USE SLICES (unused)
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
        comm = self.plugin.get_communicator()
        combined_stats = self._combine_mpi_stats(stats, comm=comm)
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
        if len(combined_stats['max']) != 0:
            stats_dict = self.calc_volume_stats(combined_stats)
            Statistics.global_residuals[p_num] = {}
            #before_processing = self.calc_volume_stats(self.stats_before_processing)
            #for key in list(before_processing.keys()):
            #    Statistics.global_residuals[p_num][key] = Statistics.global_stats[p_num][key] - before_processing[key]

            if len(Statistics.global_stats[p_num]) == 0:
                Statistics.global_stats[p_num] = [stats_dict]
            else:
                Statistics.global_stats[p_num].append(stats_dict)

            self._link_stats_to_datasets(stats_dict, self._iterative_group)
            self._write_stats_to_file(p_num, comm=comm)
        self._already_called = True
        self._repeat_count += 1
        if self._iterative_group or self._4d:
            self.stats = {stat: [] for stat in self.slice_stats_key}

    def start_time(self):
        """Called at the start of a plugin."""
        self.t0 = time.time()

    def stop_time(self):
        """Called at the ebd of a plugin."""
        self.t1 = time.time()
        elapsed = round(self.t1 - self.t0, 1)
        if self._stats_flag and self.calc_stats:
            self.set_time(elapsed)

    def set_time(self, seconds):
        """Sets time taken for plugin to complete."""
        Statistics.global_times[self.p_num] += seconds  # Gives total time for a plugin in a loop
        #print(f"{self.p_num}, {seconds}")
        comm = self.plugin.get_communicator()
        self._write_times_to_file(comm)

    def _combine_mpi_stats(self, slice_stats, comm=MPI.COMM_WORLD):
        """Combines slice stats from different processes, so volume stats can be calculated.

        :param slice_stats: slice stats (each process will have a different set).
        :param comm: MPI communicator being used.
        """
        combined_stats_list = comm.allgather(slice_stats)
        combined_stats = {stat: [] for stat in self.slice_stats_key}
        for single_stats in combined_stats_list:
            for key in self.slice_stats_key:
                combined_stats[key] += single_stats[key]
        return combined_stats

    def _array_to_dict(self, stats_array, key_list=None):
        """Converts an array of stats to a dictionary of stats.

        :param stats_array: Array of stats to be converted.
        :param key_list: List of keys indicating the names of the stats in the stats_array.
        """
        if key_list is None:
            key_list = self.stats_key
        stats_dict = {}
        for i, value in enumerate(stats_array):
            stats_dict[key_list[i]] = value
        return stats_dict

    def _dict_to_array(self, stats_dict):
        """Converts stats dict into a numpy array (keys will be lost).

        :param stats_dict: dictionary of stats.
        """
        return np.array(list(stats_dict.values()))

    def _set_pattern_info(self):
        """Gathers information about the pattern of the data in the current plugin."""
        out_datasets = self.plugin.get_out_datasets()
        if len(out_datasets) == 0:
            self.calc_stats = False
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
                    self.pattern = None
        if self.pattern not in Statistics._pattern_list:
            self.calc_stats = False

    def _link_stats_to_datasets(self, stats_dict, iterative=False):
        """Links the volume wide statistics to the output dataset(s).

        :param stats_dict: Dictionary of stats being linked.
        :param iterative: boolean indicating if the plugin is iterative or not.
        """
        out_dataset = self.plugin.get_out_datasets()[0]
        my_dataset = out_dataset
        if iterative:
            if "itr_clone" in out_dataset.group_name:
                my_dataset = list(iterative._ip_data_dict["iterating"].keys())[0]
        n_datasets = self.plugin.nOutput_datasets()

        i = 2
        group_name = "stats"
        while group_name in list(my_dataset.meta_data.get_dictionary().keys()):
            group_name = f"stats{i}"
            i += 1
        for key, value in stats_dict.items():
            my_dataset.meta_data.set([group_name, key], value)

    def _write_stats_to_file(self, p_num=None, plugin_name=None, comm=MPI.COMM_WORLD):
        """Writes stats to a h5 file. This file is used to create figures and tables from the stats.

        :param p_num: The plugin number of the plugin the stats belong to (usually left as None except
            for special cases)
        :param plugin_name: Same as above (but for the name of the plugin).
        :param comm: The MPI communicator the plugin is using.
        """
        if p_num is None:
            p_num = self.p_num
        if plugin_name is None:
            plugin_name = self.plugin_names[p_num]
        path = Statistics.path
        filename = f"{path}/stats.h5"
        stats_dict = self.get_stats(p_num, instance="all")
        stats_array = self._dict_to_array(stats_dict[0])
        stats_key = list(stats_dict[0].keys())
        for i, my_dict in enumerate(stats_dict):
            if i != 0:
                stats_array = np.vstack([stats_array, self._dict_to_array(my_dict)])
        self.hdf5 = Hdf5Utils(self.exp)
        self.exp._barrier(communicator=comm)
        if comm.rank == 0:
            with h5.File(filename, "a") as h5file:
                group = h5file.require_group("stats")
                if stats_array.shape != (0,):
                    if str(p_num) in list(group.keys()):
                        del group[str(p_num)]
                    dataset = group.create_dataset(str(p_num), shape=stats_array.shape, dtype=stats_array.dtype)
                    dataset[::] = stats_array[::]
                    dataset.attrs.create("plugin_name", plugin_name)
                    dataset.attrs.create("pattern", self.pattern)
                    dataset.attrs.create("stats_key", stats_key)
                if self._iterative_group:
                    l_stats = Statistics.loop_stats[self.l_num]
                    group1 = h5file.require_group("iterative")
                    if self._iterative_group._ip_iteration == self._iterative_group._ip_fixed_iterations - 1\
                            and self.p_num == self._iterative_group.end_index:
                        dataset1 = group1.create_dataset(str(self.l_num), shape=l_stats["NRMSD"].shape, dtype=l_stats["NRMSD"].dtype)
                        dataset1[::] = l_stats["NRMSD"][::]
                        loop_plugins = []
                        for i in range(self._iterative_group.start_index, self._iterative_group.end_index + 1):
                            if i in list(self.plugin_names.keys()):
                                loop_plugins.append(self.plugin_names[i])
                        dataset1.attrs.create("loop_plugins", loop_plugins)
                        dataset.attrs.create("n_loop_plugins", len(loop_plugins))
        self.exp._barrier(communicator=comm)

    def _write_times_to_file(self, comm):
        p_num = self.p_num
        plugin_name = self.plugin_name
        path = Statistics.path
        filename = f"{path}/stats.h5"
        time = Statistics.global_times[p_num]
        self.hdf5 = Hdf5Utils(self.exp)
        if comm.rank == 0:
            with h5.File(filename, "a") as h5file:
                group = h5file.require_group("stats")
                dataset = group[str(p_num)]
                print(time)
                dataset.attrs.create("time", time)

    def write_slice_stats_to_file(self, slice_stats=None, p_num=None, comm=MPI.COMM_WORLD):
        """Writes slice statistics to a h5 file. Placed in the stats folder in the output directory. Currently unused."""
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
        with h5.File(filename, "a", driver="mpio", comm=comm) as h5file:
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

    def _unpad_slice(self, my_slice):
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
            self._slice_list, self._pad = self._get_unpadded_slice_list(my_slice, slice_dims)
        if self._pad:
            #for slice_dim in slice_dims:
            slice_dim = slice_dims[0]
            temp_slice = np.swapaxes(my_slice, 0, slice_dim)
            temp_slice = temp_slice[self._slice_list[slice_dim]]
            my_slice = np.swapaxes(temp_slice, 0, slice_dim)
        return my_slice

    def _get_unpadded_slice_list(self, my_slice, slice_dims):
        """Creates slice object(s) to un-pad slices in the slice dimension(s)."""
        slice_list = list(self.plugin.slice_list[0])
        pad = False
        if len(slice_list) == len(my_slice.shape):
            #for i in slice_dims:
            i = slice_dims[0]
            slice_width = self.plugin.slice_list[0][i].stop - self.plugin.slice_list[0][i].start
            if slice_width < my_slice.shape[i]:
                pad = True
                pad_width = (my_slice.shape[i] - slice_width) // 2  # Assuming symmetrical padding
                slice_list[i] = slice(pad_width, pad_width + 1, 1)
            return tuple(slice_list), pad
        else:
            return self.plugin.slice_list[0], pad

    def _flatten(self, l):
        """Function to flatten nested lists."""
        out = []
        for item in l:
            if isinstance(item, (list, tuple)):
                out.extend(self._flatten(item))
            else:
                out.append(item)
        return out

    def _de_list(self, my_slice):
        """If the slice is in a list, remove it from that list."""
        if type(my_slice) == list:
            if len(my_slice) != 0:
                my_slice = my_slice[0]
                my_slice = self._de_list(my_slice)
        return my_slice

    @classmethod
    def _count(cls):
        cls.count += 1

    @classmethod
    def _post_chain(cls):
        """Called after all plugins have run."""
        if cls._any_stats & cls._stats_flag:
            stats_utils = StatsUtils()
            stats_utils.generate_figures(f"{cls.path}/stats.h5", cls.path)
