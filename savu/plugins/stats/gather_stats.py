# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: comparison
   :platform: Unix
   :synopsis: A plugin to compare two datasets, given as input datasets, and print the RMSD between the two.
              The data is unchanged.

.. moduleauthor:: Jacob Williamson <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.core.iterate_plugin_group_utils import enable_iterative_loop, \
    check_if_end_plugin_in_iterate_group, setup_extra_plugin_data_padding

import os
import h5py as h5

# This decorator is required for the configurator to recognise the plugin
@register_plugin
class GatherStats(Plugin, CpuPlugin):

    def __init__(self):
        super(GatherStats, self).__init__("GatherStats")

    def nInput_datasets(self):
        return 1


    def nOutput_datasets(self):
        return 0

    def nClone_datasets(self):
        if check_if_end_plugin_in_iterate_group(self.exp):
            return 1
        else:
            return 0


    @enable_iterative_loop
    def setup(self):

        in_dataset, out_dataset = self.get_datasets()
        self.stats_obj.calc_stats = False
        self.stats_obj.set_stats_key(["max", "min", "mean", "mean_std_dev", "median_std_dev", "zeros", "zeros%",
                                       "range_used"])
        in_pData, out_pData = self.get_plugin_datasets()

        # Each plugin dataset must call this method and define the data access
        # pattern and number of frames required.
        for i in range(len(in_pData)):
            in_pData[i].plugin_data_setup(self.parameters['pattern'], 'single')

        # All dataset information can be accessed via the Data and PluginData
        # instances


    def pre_process(self):
        # This method is called once before any processing has begun.
        # Access parameters from the doc string in the parameters dictionary
        # e.g. self.parameters['example']
        in_datasets = self.get_in_datasets()

    def process_frames(self, data):
        self.stats_obj.set_slice_stats(data, pad=False)
        return None

    def post_process(self):
        slice_stats = self.stats_obj.stats
        comm = self.get_communicator()
        combined_stats = self.stats_obj._combine_mpi_stats(slice_stats, comm=comm)

        volume_stats = self.stats_obj.calc_volume_stats(combined_stats)
        if self.exp.meta_data.get("pre_run"):

            self._generate_warnings(volume_stats)
            self.exp.meta_data.set("pre_process_stats", volume_stats)

            folder = self.exp.meta_data['out_path']
            fname = self.exp.meta_data.get('datafile_name') + '_pre_run.nxs'
            filename = os.path.join(folder, fname)
            stats_array = self.stats_obj._dict_to_array(volume_stats)
            if comm.rank == 0:
                with h5.File(filename, "a") as h5file:
                    fsplit = self.exp.meta_data["data_path"].split("/")
                    fsplit[-1] = ""
                    stats_path = "/".join(fsplit)
                    stats_group = h5file.require_group(stats_path)
                    dataset = stats_group.create_dataset("stats", shape=stats_array.shape, dtype=stats_array.dtype)
                    dataset[::] = stats_array[::]
                    dataset.attrs.create("stats_key", list(self.stats_obj.stats_key))

    def _generate_warnings(self, volume_stats):
        warnings = []
        if volume_stats["zeros%"] > 10:
            warnings.append(f"Percentage of data points that are 0s is {volume_stats['zeros%']}")
        if volume_stats["range_used"] < 2:
            warnings.append(f"Only {volume_stats['range_used']}% of the possible range of the datatype (\
{self.stats_obj.stats['dtype']}) has been used. The datatype used, {self.stats_obj.stats['dtype']} can go from \
{self.stats_obj.stats['possible_min']} to {self.stats_obj.stats['possible_max']}")
        self.exp.meta_data.set("warnings", warnings)
