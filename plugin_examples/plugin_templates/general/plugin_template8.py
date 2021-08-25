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
.. module:: plugin_template8
   :platform: Unix
   :synopsis: A template to create a simple plugin that takes one dataset as\
   input and returns a similar dataset as output.

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class PluginTemplate8(Plugin, CpuPlugin):

    def __init__(self, name="PluginTemplate8"):
        super(PluginTemplate8, self).__init__(name)
        self.nOut = None

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return len(self.parameters['out_datasets'])

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        
        for i in range(len(out_dataset)):
            out_dataset[i].create_dataset(in_dataset[0])
            out_pData[i].plugin_data_setup('SINOGRAM', 'single')

    def pre_process(self):
        pass

    def process_frames(self, data):
        # do some processing here
        return [data[0], data[0]]

    def post_process(self):
        pass