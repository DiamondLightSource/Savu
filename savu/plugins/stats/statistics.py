"""
.. module:: statistics
   :platform: Unix
   :synopsis: Contains and processes statistics information for each plugin.

.. moduleauthor::Jacob Williamson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils

import h5py as h5
import numpy as np
import os


class Statistics(object):
    _index_dict = {"max": 0, "min": 1, "mean": 2, "mean_std_dev": 3, "median_std_dev": 4}
    _key_list = ["max", "min", "mean", "mean_std_dev", "median_std_dev"]
    pattern_list = ["SINOGRAM", "PROJECTION", "VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D", "4D_SCAN", "SINOMOVIE"]
    no_stats_plugins = ["BasicOperations", "Mipmap"]

    def __init__(self):
        self.calc_stats = True

    def setup(self, plugin_self):
        if self.calc_stats:
            self.plugin = plugin_self
            self.plugin_name = plugin_self.name
            self.pad_dims = []
            self.stats = {'max': [], 'min': [], 'mean': [], 'standard_deviation': []}
            self.calc_stats = False
            self._already_called = False
            self._set_pattern_info()
            if self.plugin_name in Statistics.no_stats_plugins:
                self.calc_stats = False

    @classmethod
    def _setup_class(cls, exp):
        """Sets up the statistics class for the whole experiment (only called once)"""
        cls.count = 2
        cls.data_stats = {}
        cls.volume_stats = {}
        cls.global_stats = {}
        n_plugins = len(exp.meta_data.plugin_list.plugin_list)
        # for n in range(n_plugins):
        #    cls.data_stats[n + 1] = [None, None, None, None, None]
        #    cls.volume_stats[n + 1] = [None, None, None, None, None]
        cls.path = exp.meta_data['out_path']
        if cls.path[-1] == '/':
            cls.path = cls.path[0:-1]
        cls.path = f"{cls.path}/stats"
        if not os.path.exists(cls.path):
            os.mkdir(cls.path)

    def set_slice_stats(self, slice1):
        """Appends slice stats arrays with the stats parameters of the current slice.

        :param slice1: The slice whose stats are being calculated.
        """
        if slice1 is not None:
            slice_num = self.plugin.pcount
            slice1 = self._de_list(slice1)
            slice1 = self._unpad_slice(slice1)
            self.stats['max'].append(slice1.max())
            self.stats['min'].append(slice1.min())
            self.stats['mean'].append(np.mean(slice1))
            self.stats['standard_deviation'].append(np.std(slice1))

    def get_slice_stats(self, stat, slice_num):
        """Returns array of stats associated with the processed slices of the current plugin."""
        return self.stats[stat][slice_num]

    def set_volume_stats(self):
        """Calculates volume-wide statistics from slice stats, and updates class-wide arrays with these values.
        Links volume stats with the output dataset and writes slice stats to file.
        """
        p_num = Statistics.count
        name = self.plugin_name
        i = 2
        while name in list(Statistics.global_stats.keys()):
            name = self.plugin_name + str(i)
            i += 1
        Statistics.data_stats[p_num] = [None, None, None, None, None]
        Statistics.volume_stats[p_num] = [None, None, None, None, None]
        if len(self.stats['max']) != 0:
            if self.pattern in ['PROJECTION', 'SINOGRAM', 'TANGENTOGRAM', 'SINOMOVIE', '4D_SCAN']:
                Statistics.data_stats[p_num][0] = max(self.stats['max'])
                Statistics.data_stats[p_num][1] = min(self.stats['min'])
                Statistics.data_stats[p_num][2] = np.mean(self.stats['mean'])
                Statistics.data_stats[p_num][3] = np.mean(self.stats['standard_deviation'])
                Statistics.data_stats[p_num][4] = np.median(self.stats['standard_deviation'])
                Statistics.global_stats[p_num] = Statistics.data_stats[p_num]
                Statistics.global_stats[name] = Statistics.global_stats[p_num]
                self._link_stats_to_datasets(Statistics.global_stats[name])
            elif self.pattern in ['VOLUME_XZ', 'VOLUME_XY', 'VOLUME_YZ', 'VOLUME_3D']:
                Statistics.volume_stats[p_num][0] = max(self.stats['max'])
                Statistics.volume_stats[p_num][1] = min(self.stats['min'])
                Statistics.volume_stats[p_num][2] = np.mean(self.stats['mean'])
                Statistics.volume_stats[p_num][3] = np.mean(self.stats['standard_deviation'])
                Statistics.volume_stats[p_num][4] = np.median(self.stats['standard_deviation'])
                Statistics.global_stats[p_num] = Statistics.volume_stats[p_num]
                Statistics.global_stats[name] = Statistics.global_stats[p_num]
                self._link_stats_to_datasets(Statistics.global_stats[name])
        slice_stats = np.array([self.stats['max'], self.stats['min'], self.stats['mean'],
                                self.stats['standard_deviation']])
        self._write_stats_to_file(slice_stats, p_num)
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
        if stat is not None:
            i = Statistics._index_dict[stat]
            return Statistics.global_stats[name][i]
        else:
            stats = dict(zip(Statistics._key_list, Statistics.global_stats[name]))
            return stats

    def get_stats_from_num(self, p_num, stat=None):
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
        if stat is not None:
            i = Statistics._index_dict[stat]
            return Statistics.global_stats[p_num][i]
        else:
            stats = dict(zip(Statistics._key_list, Statistics.global_stats[p_num]))
            return stats

    def get_stats_from_dataset(self, dataset, stat=None, set_num=None):
        """Returns stats associated with a dataset.

        :param dataset: The dataset whose associated stats are being fetched.
        :param stat: Specify the stat parameter you want to fetch, i.e 'max', 'mean', 'median_std_dev'.
            If left blank will return the whole dictionary of stats:
            {'max': , 'min': , 'mean': , 'mean_std_dev': , 'median_std_dev': }
        :param set_num: In the (rare) case that there are multiple sets of stats associated with the dataset,
            specify which set to return.

        """
        key = "stats"
        stats = {}
        if set_num is not None and set_num not in (0, 1):
            key = key + str(set_num)
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
        for dataset in out_datasets:
            if bool(set(Statistics.pattern_list) & set(dataset.data_info.get("data_patterns"))):
                self.calc_stats = True

    def _link_stats_to_datasets(self, stats):
        """Links the volume wide statistics to the output dataset(s)"""
        out_dataset = self.plugin.get_out_datasets()[0]
        n_datasets = self.plugin.nOutput_datasets()
        i = 2
        group_name = "stats"
        if n_datasets == 1:
            while group_name in list(out_dataset.meta_data.get_dictionary().keys()):
                group_name = f"stats{i}"
                i += 1
            out_dataset.meta_data.set([group_name, "max"], stats[0])
            out_dataset.meta_data.set([group_name, "min"], stats[1])
            out_dataset.meta_data.set([group_name, "mean"], stats[2])
            out_dataset.meta_data.set([group_name, "mean_std_dev"], stats[3])
            out_dataset.meta_data.set([group_name, "median_std_dev"], stats[4])

    def _write_stats_to_file(self, slice_stats, p_num):
        """Writes slice statistics to a h5 file"""
        path = Statistics.path
        filename = f"{path}/stats_p{p_num}_{self.plugin_name}.h5"
        slice_stats_dim = (slice_stats.shape[1],)
        self.hdf5 = Hdf5Utils(self.plugin.exp)
        with h5.File(filename, "a") as h5file:
            i = 2
            group_name = "/stats"
            while group_name in h5file:
                group_name = f"/stats{i}"
                i += 1
            group = h5file.create_group(group_name, track_order=None)
            max_ds = self.hdf5.create_dataset_nofill(group, "max", slice_stats_dim, slice_stats.dtype)
            min_ds = self.hdf5.create_dataset_nofill(group, "min", slice_stats_dim, slice_stats.dtype)
            mean_ds = self.hdf5.create_dataset_nofill(group, "mean", slice_stats_dim, slice_stats.dtype)
            standard_deviation_ds = self.hdf5.create_dataset_nofill(group, "standard_deviation",
                                                                    slice_stats_dim, slice_stats.dtype)
            max_ds[::] = slice_stats[0]
            min_ds[::] = slice_stats[1]
            mean_ds[::] = slice_stats[2]
            standard_deviation_ds[::] = slice_stats[3]

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
            for slice_dim in slice_dims:
                temp_slice = np.swapaxes(slice1, 0, slice_dim)
                temp_slice = temp_slice[self.slice_list[slice_dim]]
                slice1 = np.swapaxes(temp_slice, 0, slice_dim)
        return slice1

    def _get_unpadded_slice_list(self, slice1, slice_dims):
        """Creates slice object(s) to un-pad slices in the slice dimension(s)."""
        slice_list = list(self.plugin.slice_list[0])
        pad = False
        if len(slice_list) == len(slice1.shape):
            for i in slice_dims:
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
        print(cls.data_stats)
        print(cls.volume_stats)
        print(cls.global_stats)