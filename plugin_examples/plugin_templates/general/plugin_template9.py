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
.. module:: plugin_template9
   :platform: Unix
   :synopsis: A template to create a simple plugin that takes one dataset as\
   input and returns a similar dataset as output.

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class PluginTemplate9(Plugin, CpuPlugin):

    def __init__(self, name="PluginTemplate9"):
        super(PluginTemplate9, self).__init__(name)

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        nOut = self.parameters['n_out']
        # the output datasets do not yet have names so add them here
        name = self.parameters['out_prefix']
        # update the out_datasets list to contain the uniquely named datasets
        self.parameters['out_datasets'] = ['%s_%i' % (name, i) for i in range(nOut)]
        return nOut

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        
        for i in range(len(out_dataset)):
            out_dataset[i].create_dataset(in_dataset[0])
            out_pData[i].plugin_data_setup('SINOGRAM', 'single')

    def pre_process(self):
        out_datasets = self.get_out_datasets()
        self.nOut = len(out_datasets)

    def process_frames(self, data):
        # do some processing here
        res = [data[0]]*self.nOut
        return res

    def post_process(self):
        pass