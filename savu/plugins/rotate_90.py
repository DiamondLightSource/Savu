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
.. module:: rotate_90
   :platform: Unix
   :synopsis: (Change this) A template to create a simple plugin that takes 
    one dataset as input and returns a similar dataset as output.

.. moduleauthor:: (Change this) Developer Name <email@address.ac.uk>
"""
from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin

import numpy as np

@register_plugin
class Rotate90(Plugin, CpuPlugin):
# Each class must inherit from the Plugin class and a driver

    def __init__(self):
        super(Rotate90, self).__init__("Rotate90")

    def nInput_datasets(self):
        # Called immediately after the plugin is loaded in to the framework
        return 1


    def nOutput_datasets(self):
        # Called immediately after the plugin is loaded in to the framework
        return 1


    def setup(self):

        in_dataset, out_dataset = self.get_datasets()

        out_dataset[0].create_dataset(in_dataset[0].swapaxes(1, 2))

        in_pData, out_pData = self.get_plugin_datasets()

        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

        # All dataset information can be accessed via the Data and PluginData
        # instances


    def pre_process(self):
        # This method is called once before any processing has begun.
        # Access parameters from the doc string in the parameters dictionary
        # e.g. self.parameters['example']
        pass


    def process_frames(self, data):
        if self.parameters["direction"] == "ACW":
            data[0] = np.rot90(data[0], axes=(0, 1))
        elif self.parameters["direction"] == "CW":
            data[0] = np.rot90(data[0], axes=(1, 0))

        return data[0]


    def post_process(self):
        # This method is called once after all processing has completed
        # (after an MPI barrier).
        pass

