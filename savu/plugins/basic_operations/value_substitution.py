# Copyright 2019 Diamond Light Source Ltd.
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
.. module:: value_substitution
   :platform: Unix
   :synopsis: looks for a specific value in the provided second dataset (e.g. a mask image)\
    and substitutes it with a given value

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""


from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np

@register_plugin
class ValueSubstitution(Plugin, CpuPlugin):

    def __init__(self):
        super(ValueSubstitution, self).__init__("ValueSubstitution")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        pattern_type=self.parameters['pattern']
        in_pData[0].plugin_data_setup(pattern_type, 'single')
        in_pData[1].plugin_data_setup(pattern_type, 'single')

        out_dataset[0].create_dataset(in_dataset[0])
        out_pData[0].plugin_data_setup(pattern_type, 'single')

    def process_frames(self, data):
        indeces = np.where(data[1] == self.parameters['seek_value'])
        corr_data = np.copy(data[0])
        corr_data[indeces] = self.parameters['new_value']
        return corr_data

    def nInput_datasets(self):
        return 2

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'
