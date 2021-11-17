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
        self.exp = plugin_self.exp
        self.plugin_name = plugin_self.name
        self.pattern = plugin_self.parameters['pattern']
        self.stats = {'max': [], 'min': [], 'mean': [], 'standard_deviation': []}
        if not self.has_setup:
            self._setup(self.exp)

    @classmethod
    def _setup(cls, exp):
        cls.current_plugin = 1
        cls.data_stats = {}
        cls.volume_stats = {}
        n_plugins = exp.meta_data.plugin_list.n_plugins
        for n in range(n_plugins):
            cls.data_stats[n + 1] = [None, None, None, None]
            cls.volume_stats[n + 1] = [None, None, None, None]
        os.mkdir(f"{exp.meta_data['out_path']}/stats")
        cls.has_setup = True

    def set_slice_stats(self, slice):
        self.stats['max'].append(slice.max())
        self.stats['min'].append(slice.min())
        self.stats['mean'].append(np.mean(slice))
        self.stats['standard_deviation'].append(np.std(slice))

    def set_volume_stats(self):
        Statistics.current_plugin += 1
        p_num = Statistics.current_plugin
        if self.pattern in ['PROJECTION', 'SINOGRAM']:
            Statistics.data_stats[p_num][0] = max(self.stats['max'])
            Statistics.data_stats[p_num][1] = min(self.stats['min'])
            Statistics.data_stats[p_num][2] = np.mean(self.stats['mean'])
            # self.volume_stats[p_num][3] = np.mean(self.stats['standard_deviation'])
        elif self.pattern in ['VOLUME_XZ', 'VOLUME_XY', 'VOLUME_YZ']:
            Statistics.volume_stats[p_num][0] = max(self.stats['max'])
            Statistics.volume_stats[p_num][1] = min(self.stats['min'])
            Statistics.volume_stats[p_num][2] = np.mean(self.stats['mean'])
            #self.volume_stats[p_num][3] = np.mean(self.stats['standard_deviation'])
        slice_stats = np.array([self.stats['max'], self.stats['min'], self.stats['mean'], self.stats['standard_deviation']])
        self._write_stats_to_file(slice_stats, p_num)

    def _write_stats_to_file(self, slice_stats, p_num):
        path = f"{self.exp.meta_data['out_path']}/stats"
        filename = f"{path}/stats_p{p_num}_{self.plugin_name}.h5"
        slice_stats_dim = (slice_stats.shape[1],)
        self.hdf5 = Hdf5Utils(self.exp)
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