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

import numpy as np

# This decorator is required for the configurator to recognise the plugin
@register_plugin
class Comparison(Plugin, CpuPlugin):
# Each class must inherit from the Plugin class and a driver

    def __init__(self):
        super(Comparison, self).__init__("Comparison")

    def nInput_datasets(self):
        # Called immediately after the plugin is loaded in to the framework
        return 2


    def nOutput_datasets(self):
        # Called immediately after the plugin is loaded in to the framework
        if check_if_end_plugin_in_iterate_group(self.exp):
            return 3
        else:
            return 2

        # total number of output datasets that are clones
    def nClone_datasets(self):
        if check_if_end_plugin_in_iterate_group(self.exp):
            return 1
        else:
            return 0


    @enable_iterative_loop
    def setup(self):
        # This method is called after the number of in/out datasets associated
        # with the plugin has been established.  It tells the framework all
        # the information it needs to know about the data transport to-and-from
        # the plugin.

        # ================== Input and output datasets =========================
        # in_datasets and out_datasets are instances of the Data class.
        # in_datasets were either created in the loader or as output from
        # previous plugins.  out_datasets objects have already been created at
        # this point, but they are empty and need to be populated.

        # Get the Data instances associated with this plugin
        in_dataset, out_dataset = self.get_datasets()

        # see https://savu.readthedocs.io/en/latest/api/savu.data.data_structures.data_create/
        # for more information on creating datasets.

        # Populate the output dataset(s)
        out_dataset[0].create_dataset(in_dataset[0])
        out_dataset[1].create_dataset(in_dataset[1])
        self.rss_list = []
        self.flipped_rss_list = []
        self.data_points_list = []
        # ================== Input and output plugin datasets ==================
        # in_pData and out_pData are instances of the PluginData class.
        # All in_datasets and out_datasets above have an in/out_pData object
        # attached to them temporarily for the duration of the plugin,
        # giving access to additional plugin-specific dataset details. At this
        # point they have been created but not yet populated.

        # Get the PluginData instances attached to the Data instances above
        in_pData, out_pData = self.get_plugin_datasets()

        # Each plugin dataset must call this method and define the data access
        # pattern and number of frames required.
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        in_pData[1].plugin_data_setup(self.parameters['pattern'], 'single')

        # 'single', 'multiple' or an int (should only be used if essential)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[1].plugin_data_setup(self.parameters['pattern'], 'single')

        # All dataset information can be accessed via the Data and PluginData
        # instances


    def pre_process(self):
        # This method is called once before any processing has begun.
        # Access parameters from the doc string in the parameters dictionary
        # e.g. self.parameters['example']
        in_datasets = self.get_in_datasets()
        self.names = [in_datasets[0].group_name, in_datasets[1].group_name]
        if not self.names[0]:
            self.names[0] = "dataset1"
        if not self.names[1]:
            self.names[1] = "dataset2"

        stats = [{}, {}]
        try:
            stats[0] = self.stats_obj.get_stats_from_dataset(in_datasets[0])
        except KeyError:
            print(f"Can't find min and max metadata in {self.names[0]}, having to calculate")
            stats[0]["min"] = np.min(in_datasets[0].data[()])
            stats[0]["max"] = np.max(in_datasets[0].data[()])
        try:
            stats[1] = self.stats_obj.get_stats_from_dataset(in_datasets[1])
        except KeyError:
            print(f"Can't find min and max metadata in {self.names[1]}, having to calculate")
            stats[1]["min"] = np.min(in_datasets[1].data[()])
            stats[1]["max"] = np.max(in_datasets[1].data[()])
        self.mins = (stats[0]["min"], stats[1]["min"])
        self.ranges = (stats[0]["max"] - stats[0]["min"], stats[1]["max"] - stats[1]["min"])


    def process_frames(self, data):
        # This function is called in a loop by the framework until all the
        # data has been processed.

        # Each iteration of the loop will receive a list of numpy arrays
        # (data) containing nInput_datasets with the data sliced as requested
        # in the setup method (SINOGRAM in this case).  If 'multiple' or an
        # integer number of max_frames are requested the array with have an
        # extra dimension.

        # This plugin has one output dataset, so a single numpy array (a
        # SINOGRAM in this case) should be returned to the framework.
        if data[0].shape == data[1].shape:
            scaled_data = [self._scale_data(data[0], self.mins[0], self.ranges[0]),
                           self._scale_data(data[1], self.mins[1], self.ranges[1])]
            self.rss_list.append(self.stats_obj.calc_rss(scaled_data[0], scaled_data[1]))
            self.data_points_list.append(data[0].size)
            flipped_data = 1 - scaled_data[0]
            self.flipped_rss_list.append(self.stats_obj.calc_rss(flipped_data, scaled_data[1]))
        else:
            print("Arrays different sizes, can't calculated residuals.")
        return [data[0], data[1]]

    def _scale_data(self, data, vol_min, vol_range): # scale data slice to be between 0 and 1
        data = data - vol_min
        data = data * (1/vol_range)
        return data

    def post_process(self):

        total_rss = sum(self.rss_list)
        total_data = sum(self.data_points_list)
        RMSD = self.stats_obj.rmsd_from_rss(total_rss, total_data)
        print(f"Normalised root mean square deviation between {self.names[0]} and {self.names[1]} is {RMSD}")

        total_flipped_rss = sum(self.flipped_rss_list)
        FRMSD = self.stats_obj.rmsd_from_rss(total_flipped_rss, total_data)
        print(f"Normalised root mean square deviation between {self.names[0]} and {self.names[1]} is {FRMSD}, \
              when the contrast is flipped")

