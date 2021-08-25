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
.. module:: elementwise_arrays_arithmetics
   :platform: Unix
   :synopsis: perform elementwise arithmetic operations on two input datasets: addition, subtraction, multiplication and division

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""


from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np

@register_plugin
class ElementwiseArraysArithmetics(Plugin, CpuPlugin):
    def __init__(self):
        super(ElementwiseArraysArithmetics, self).__init__("ElementwiseArraysArithmetics")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        pattern_type=self.parameters['pattern']
        in_pData[0].plugin_data_setup(pattern_type, 'single')
        in_pData[1].plugin_data_setup(pattern_type, 'single')

        out_dataset[0].create_dataset(in_dataset[0])
        out_pData[0].plugin_data_setup(pattern_type, 'single')

    def process_frames(self, data):
        if (self.parameters['operation'] == 'addition'):
            corr_data = data[0] + data[1]
        if (self.parameters['operation'] == 'subtraction'):
            corr_data = data[0] - data[1]
        if (self.parameters['operation'] == 'multiplication'):
            corr_data = np.multiply(data[0], data[1])
        if (self.parameters['operation'] == 'division'):
            corr_data = np.true_divide(data[0], data[1])
        return corr_data

    def nInput_datasets(self):
        return 2

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'
