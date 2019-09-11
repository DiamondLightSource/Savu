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
 .. module:: perform elemetary arithmetic operations on data: addition, subtraction, multiplication and division
   :platform: Unix
   :synopsis: perform elemetary arithmetic operations on data: addition, subtraction, multiplication and division

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

#:param input_vector: A vector for subsequent vector to scalar operation, specify the data name. Default: None.

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np

@register_plugin
class ArithmeticOperations(Plugin, CpuPlugin):
    """
    Basic arithmetic operations on data: addition, subtraction, multiplication and division.\
    Operations can be performed by providing a scalar value or a vector of values from which \
    vector->scalar operation (e.g. min, max, mean etc.) must be performed first.
    
    :param scalar_value: A scalar value value for arithmetic operation. Default: None.
    :param operation: arithmetic operation to apply to data, choose from addition, subtraction, multiplication and division. Default: 'addition'.    
    :param vector_operation: Vector operation to be applied to input vector, choose min, max, mean. Default: 'max'.
    """

    def __init__(self):
        super(ArithmeticOperations, self).__init__("ArithmeticOperations")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_XZ', 'single')
        out_pData[0].plugin_data_setup('VOLUME_XZ', 'single')

        #data_t = self.get_in_datasets()[0]
        #name = data_t.get_name()
        #self.my_vector = in_dataset[0].meta_data.get()
        self.my_vector = [1.0, 2.0]
        #print(temp_vector)
        
    def pre_process(self):
        #perform vector -> scalar operation
        if (self.parameters['scalar_value'] is not None):
            # working with a provided scalar
            self.scalar_res = self.parameters['scalar_value']
        else:
            # working with METADATA
            if (self.parameters['vector_operation'] == 'min'):
                self.scalar_res = np.min(self.my_vector)
            if (self.parameters['vector_operation'] == 'max'):
                self.scalar_res = np.max(self.my_vector)
            if (self.parameters['vector_operation'] == 'mean'):
                self.scalar_res = np.mean(self.my_vector)
    def process_frames(self, data):
        if (self.parameters['operation'] == 'addition'):
            corr_data = data[0] + self.scalar_res
        if (self.parameters['operation'] == 'subtraction'):
            corr_data = data[0] - self.scalar_res
        if (self.parameters['operation'] == 'multiplication'):
            corr_data = np.multiply(data[0], self.scalar_res)
        if (self.parameters['operation'] == 'division'):
            corr_data = np.true_divide(data[0], self.scalar_res)
        return corr_data
    def nOutput_datasets(self):
        return 1
    def get_max_frames(self):
        return 'single'