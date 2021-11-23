"""
.. module:: statistics
   :platform: Unix
   :synopsis: Contains and processes statistics information for each plugin

.. moduleauthor::Jacob Williamson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils

import h5py as h5
import numpy as np
import os

class Statistics(object):

    has_setup = False

    def __init__(self, plugin_self):
        self.plugin = plugin_self
        self.plugin_name = plugin_self.name
        try:
            self.pattern = plugin_self.parameters['pattern']
        except KeyError:
            self.pattern = 'VOLUME_XZ'
        self.stats = {'max': [], 'min': [], 'mean': [], 'standard_deviation': []}
        if not self.has_setup:
            Statistics._setup(self.plugin.exp)

    @classmethod
    def _setup(cls, exp):
        cls.count = 1
        cls.data_stats = {}
        cls.volume_stats = {}
        n_plugins = exp.meta_data.plugin_list.n_plugins
        for n in range(n_plugins):
            cls.data_stats[n + 1] = [None, None, None, None]
            cls.volume_stats[n + 1] = [None, None, None, None]
        os.mkdir(f"{exp.meta_data['out_path']}/stats")
        cls.has_setup = True

    def set_slice_stats(self, slice):
        #slice = self._unpad_slice(slice)
        self.stats['max'].append(slice.max())
        self.stats['min'].append(slice.min())
        self.stats['mean'].append(np.mean(slice))
        self.stats['standard_deviation'].append(np.std(slice))

    def set_volume_stats(self):
        Statistics.count += 1
        p_num = Statistics.count
        if self.pattern in ['PROJECTION', 'SINOGRAM', 'TANGENTOGRAM']:
            Statistics.data_stats[p_num][0] = max(self.stats['max'])
            Statistics.data_stats[p_num][1] = min(self.stats['min'])
            Statistics.data_stats[p_num][2] = np.mean(self.stats['mean'])
            #self.volume_stats[p_num][3] = np.mean(self.stats['standard_deviation'])
        elif self.pattern in ['VOLUME_XZ', 'VOLUME_XY', 'VOLUME_YZ']:
            Statistics.volume_stats[p_num][0] = max(self.stats['max'])
            Statistics.volume_stats[p_num][1] = min(self.stats['min'])
            Statistics.volume_stats[p_num][2] = np.mean(self.stats['mean'])
            #self.volume_stats[p_num][3] = np.mean(self.stats['standard_deviation'])
        slice_stats = np.array([self.stats['max'], self.stats['min'], self.stats['mean'], self.stats['standard_deviation']])
        self._write_stats_to_file(slice_stats, p_num)
        if p_num == self.plugin.exp.meta_data.plugin_list.n_plugins:
            Statistics._post_chain()

    def _write_stats_to_file(self, slice_stats, p_num):
        path = f"{self.plugin.exp.meta_data['out_path']}/stats"
        filename = f"{path}/stats_p{p_num}_{self.plugin_name}.h5"
        slice_stats_dim = (slice_stats.shape[1],)
        self.hdf5 = Hdf5Utils(self.plugin.exp)
        with h5.File(filename, "a") as h5file:
            group = h5file.create_group("/stats", track_order=None)
            max_ds = self.hdf5.create_dataset_nofill(group, "max", slice_stats_dim, slice_stats.dtype)
            min_ds = self.hdf5.create_dataset_nofill(group, "min", slice_stats_dim, slice_stats.dtype)
            mean_ds = self.hdf5.create_dataset_nofill(group, "mean", slice_stats_dim, slice_stats.dtype)
            standard_deviation_ds = self.hdf5.create_dataset_nofill(group, "standard_deviation", slice_stats_dim, slice_stats.dtype)
            max_ds[::] = slice_stats[0]
            min_ds[::] = slice_stats[1]
            mean_ds[::] = slice_stats[2]
            standard_deviation_ds[::] = slice_stats[3]

    def _unpad_slice(self, slice):
        if self.plugin.pcount == 0:
            self.pad_dims = []
            for i in range(len(self.plugin.slice_list)):
                if (self.plugin.slice_list[0][i].stop - self.plugin.slice_list[0][i].start) != slice.shape[i]:
                    self.pad_dims.append(i)
        #pad_dim = self.plugin.data_objs.get_slice_dimensions()
        #slice = slice[slice_list]
        return slice

    @classmethod
    def _post_chain(cls):
        print(cls.data_stats)
        print(cls.volume_stats)
