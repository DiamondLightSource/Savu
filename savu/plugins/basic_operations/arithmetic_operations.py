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
.. module:: arithmetic_operations
   :platform: Unix
   :synopsis: Perform elementary arithmetic operations on data: addition,\
       subtraction, multiplication and division

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""


from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np

@register_plugin
class ArithmeticOperations(Plugin, CpuPlugin):


    def __init__(self):
        super(ArithmeticOperations, self).__init__("ArithmeticOperations")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        pattern = list(in_dataset[0].get_data_patterns().keys())[0]
        in_pData[0].plugin_data_setup(pattern, self.get_max_frames())
        out_pData[0].plugin_data_setup(pattern, self.get_max_frames())

    def pre_process(self):
        data = self.get_in_datasets()[0]
        self.scalar_res = 0.0
        try:
            the_max = data.meta_data.get(['stats', 'max', 'pattern'])
        except KeyError:
            the_max = self.parameters['scalar_value']
        try:
            the_min = data.meta_data.get(['stats', 'min', 'pattern'])
        except KeyError:
            the_min = self.parameters['scalar_value']
        try:
            the_mean = data.meta_data.get(['stats', 'mean', 'pattern'])
        except KeyError:
            the_mean = self.parameters['scalar_value']
        # working with METADATA
        if (self.parameters['metadata_value'] == 'min'):
            if (the_min is not None):
                self.scalar_res = the_min
        if (self.parameters['metadata_value'] == 'max'):
            if (the_max is not None):
                self.scalar_res = the_max
        if (self.parameters['metadata_value'] == 'mean'):
            if (the_mean is not None):
                self.scalar_res = the_mean

    def process_frames(self, data):
        if (self.scalar_res != 0.0):
            if (self.parameters['operation'] == 'addition'):
                corr_data = data[0] + self.scalar_res
            if (self.parameters['operation'] == 'subtraction'):
                corr_data = data[0] - self.scalar_res
            if (self.parameters['operation'] == 'multiplication'):
                corr_data = np.multiply(data[0], self.scalar_res)
            if (self.parameters['operation'] == 'division'):
                corr_data = np.true_divide(data[0], self.scalar_res)
        return corr_data

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'multiple'
