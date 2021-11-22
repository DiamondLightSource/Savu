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
.. module:: plugin_template6
   :platform: Unix
   :synopsis: A template to create a plugin that changes the shape of the data.

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""
import numpy as np

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class PluginTemplate6(Plugin, CpuPlugin):

    def __init__(self):
        super(PluginTemplate6, self).__init__('PluginTemplate6')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def setup(self):
        # get all in and out datasets required by the plugin
        in_dataset, self.out_dataset = self.get_datasets()

        # set in_plugin_dataset first so pattern information is available to
        # calculate the new shape
        self.in_pData, self.out_pData = self.get_plugin_datasets()
        pattern = self.parameters['pattern']
        self.in_pData[0].plugin_data_setup(pattern, 'single')

        # calculate the output shape (based on the input shape)
        self.out_shape = \
            self.new_shape(in_dataset[0].get_shape(), in_dataset[0])

        #=================== populate output datasets =========================
        # the output data shape retains the same patterns and axis labels but
        # requires a different shape.
        self.out_dataset[0].create_dataset(patterns=in_dataset[0],
                                           axis_labels=in_dataset[0],
                                           shape=self.out_shape)

        #================== populate output plugin datasets ===================
        self.out_pData[0].plugin_data_setup(pattern, 'single')

    def new_shape(self, full_shape, data):
        # example of a function to calculate a new output data shape based on
        # the input data shape
        core_dirs = data.get_core_dimensions()
        new_shape = list(full_shape)
        for dim in core_dirs:
            new_shape[dim] = full_shape[dim] // self.parameters['bin_size']
        return tuple(new_shape)

    def pre_process(self):
        # Example of calculating a new slice list to reduce the data
        in_data_shape = self.in_pData[0].get_shape()
        bin_size = self.parameters['bin_size']
        new_sl = [slice(0, i, bin_size) for i in in_data_shape]

        # update all axis label values based on the new slice list
        self.out_dataset[0].amend_axis_label_values(
            self.out_pData[0]._get_data_slice_list(new_sl))

    def process_frames(self, data):
        # replace this with your function
        return np.zeros(self.get_plugin_out_datasets()[0].get_shape())

    def post_process(self):
        pass
