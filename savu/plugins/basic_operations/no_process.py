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
.. module:: no_process
   :platform: Unix
   :synopsis: Plugin to test loading and saving without processing
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class NoProcess(Plugin, CpuPlugin):
    """
---
          - name: NoProcess
            verbose: A test plugin for parameter types.
            parameters:
               - pattern:
                    visibility: not_param
                    type: str
                    description: Explicitly state the slicing pattern.
                    default: None
               - other:
                    visibility: param
                    type: int
                    description: Dummy parameter for testing.
                    default: 10
    """

    def __init__(self):
        super(NoProcess, self).__init__("NoProcess")

    def process_frames(self, data):
        return data[0]

    def setup(self):
        """
        Initial setup of all datasets required as input and output to the
        plugin.  This method is called before the process method in the plugin
        chain.
        """
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()

        if self.parameters['pattern']:
            pattern = self.parameters['pattern']
        else:
            pattern = in_dataset[0].get_data_patterns().keys()[0]

        in_pData[0].plugin_data_setup(pattern, self.get_max_frames())
        out_pData[0].plugin_data_setup(pattern, self.get_max_frames())

    def get_max_frames(self):
        return 'multiple'

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

        '''
           The base class from which all plugins should inherit.
           :u*param pattern: Explicitly state the slicing pattern. Default: None.
           :param dummy: Dummy parameter for testing. Default: 10.
        '''