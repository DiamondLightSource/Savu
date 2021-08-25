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
.. module:: plugin_template4
   :platform: Unix
   :synopsis: A template for a plugin that takes in two datasets and returns\
       one dataset.

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class PluginTemplate4(Plugin, CpuPlugin):

    def __init__(self):
        super(PluginTemplate4, self).__init__('PluginTemplate4')

    def nInput_datasets(self):
        return 2

    def nOutput_datasets(self):
        return 1

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])

        in_pData, out_pData = self.get_plugin_datasets()

        # example of getting information from the dataset metadata dictionary
        # this may have been populated by a previous plugin
        mData = in_dataset[0].meta_data
        if 'PeakEnergy' in list(mData.get_dictionary().keys()):
            nChannels = mData.get('PeakEnergy')
        else:
            nChannels = 4096  # for test data

        self.set_preview(in_dataset[1], self.parameters['preview'])

        print(out_dataset[0].get_axis_labels())

        in_pData[0].plugin_data_setup('SINOGRAM', nChannels)
        in_pData[1].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', nChannels)

    def pre_process(self):
        pass

    def process_frames(self, data):
        # do some processing here with data[0] and data[1]
        return data[0]

    def post_process(self):
        pass
