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
    pattern_list = ["SINOGRAM", "PROJECTION", "VOLUME_YZ", "VOLUME_XZ", "VOLUME_XY", "VOLUME_3D", "4D_SCAN", "SINOMOVIE"]
    no_stats_plugins = ["BasicOperations", "Mipmap"]

    def __init__(self):
        self.calc_stats = True
        self.stats = {'max': [], 'min': [], 'mean': [], 'std_dev': [], 'RSS': [], 'data_points': []}
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


    @classmethod
    def _setup_class(cls, exp):
        """Sets up the statistics class for the whole experiment (only called once)"""
        cls.count = 2
        cls.data_stats = {}
        cls.volume_stats = {}
        cls.global_stats = {}
        cls.global_residuals = {}
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

    def _calc_rss(self, array1, array2): # residual sum of squares
        if array1.shape == array2.shape:
            residuals = np.subtract(array1, array2)
            rss = sum(value**2 for value in np.nditer(residuals))
        else:
            print("Warning: cannot calculate RSS, arrays different sizes.")  # need to make this an actual warning
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

    def set_slice_stats(self, slice_stats):
        """Appends slice stats arrays with the stats parameters of the current slice.

        :param slice_stats: The stats for the current slice.
        """
        self.stats['max'].append(slice_stats['max'])
        self.stats['min'].append(slice_stats['min'])
        self.stats['mean'].append(slice_stats['mean'])
        self.stats['std_dev'].append(slice_stats['std_dev'])
        self.stats['RSS'].append(slice_stats['RSS'])
        self.stats['data_points'].append(slice_stats['data_points'])

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
        Statistics.global_stats[p_num] = {}
        if len(self.stats['max']) != 0:
            Statistics.global_stats[p_num]['max'] = max(self.stats['max'])
            Statistics.global_stats[p_num]['min'] = min(self.stats['min'])
            Statistics.global_stats[p_num]['mean'] = np.mean(self.stats['mean'])
            Statistics.global_stats[p_num]['mean_std_dev'] = np.mean(self.stats['std_dev'])
            Statistics.global_stats[p_num]['median_std_dev'] = np.median(self.stats['std_dev'])
            if None not in self.stats['RSS']:
                total_rss = sum(self.stats['RSS'])
                n = sum(self.stats['data_points'])
                Statistics.global_stats[p_num]['RMSD'] = self._rmsd_from_rss(total_rss, n)
            else:
                Statistics.global_stats[p_num]['RMSD'] = None

            Statistics.global_stats[name] = Statistics.global_stats[p_num]
            self._link_stats_to_datasets(Statistics.global_stats[name])

        slice_stats_array = np.array([self.stats['max'], self.stats['min'], self.stats['mean'], self.stats['std_dev']])

        #if None not in self.stats['RMSD']:
        #    slice_stats_array = np.append(slice_stats_array, self.stats['RMSD'], 0)
        self._write_stats_to_file(slice_stats_array, p_num)
        self.set_volume_residuals()
        self._already_called = True

    def set_volume_residuals(self):
        p_num = Statistics.count
        Statistics.global_residuals[p_num] = {}
        Statistics.global_residuals[p_num]['max'] = np.mean(self.residuals['max'])
        Statistics.global_residuals[p_num]['min'] = np.mean(self.residuals['min'])
        Statistics.global_residuals[p_num]['mean'] = np.mean(self.residuals['mean'])
        Statistics.global_residuals[p_num]['std_dev'] = np.mean(self.residuals['std_dev'])

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
            return Statistics.global_stats[name][stat]
        else:
            return Statistics.global_stats[name]

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
            return Statistics.global_stats[p_num][stat]
        else:
            return Statistics.global_stats[p_num]

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
        self.calc_stats = False
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
            out_dataset.meta_data.set([group_name, "max"], stats["max"])
            out_dataset.meta_data.set([group_name, "min"], stats["min"])
            out_dataset.meta_data.set([group_name, "mean"], stats["mean"])
            out_dataset.meta_data.set([group_name, "mean_std_dev"], stats["mean_std_dev"])
            out_dataset.meta_data.set([group_name, "median_std_dev"], stats["median_std_dev"])
            if stats["RMSD"] is not None:
                out_dataset.meta_data.set([group_name, "RMSD"], stats["RMSD"])

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
        print(cls.global_residuals)