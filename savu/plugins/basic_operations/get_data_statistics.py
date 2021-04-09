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
.. module:: get_data_statistics
   :platform: Unix
   :synopsis: A plugin to calculate global statistics (max, min, sum, mean) of the input data

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np

@register_plugin
class GetDataStatistics(Plugin, CpuPlugin):
    def __init__(self):
        super(GetDataStatistics, self).__init__("GetDataStatistics")

    def setup(self):

        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        pattern_type=self.parameters['pattern']
        in_pData[0].plugin_data_setup(pattern_type, 'single')
        out_dataset[0].create_dataset(in_dataset[0])
        out_pData[0].plugin_data_setup(pattern_type, 'single')

        fullData = in_dataset[0]
        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        self.new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 4)
        out_dataset[1].create_dataset(shape=self.new_shape,
                                      axis_labels=['stattype', 'value'],
                                      remove=True,
                                      transport='hdf5')
        out_dataset[1].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[1].plugin_data_setup('METADATA', self.get_max_frames())

    def process_frames(self, data):
        data_temp = data[0]
        indices = np.where(np.isnan(data_temp))
        data_temp[indices] = 0.0
        # collecting values for each slice
        slice_values = [np.max(data_temp), np.min(data_temp), np.sum(data_temp), np.mean(data_temp)]
        return [data_temp, np.array([slice_values])]

    def post_process(self):
        data, slice_values = self.get_out_datasets()
        all_slice_values = slice_values.data[...]
        max_stat = np.max(all_slice_values[:,0])
        min_stat = np.max(all_slice_values[:,1])
        sum_stat = np.sum(all_slice_values[:,2])
        mean_stat = np.sum(all_slice_values[:,3])
        data.meta_data.set(['stats', 'max', 'pattern'], max_stat)
        data.meta_data.set(['stats', 'min', 'pattern'], min_stat)
        data.meta_data.set(['stats', 'sum', 'pattern'], sum_stat)
        data.meta_data.set(['stats', 'mean', 'pattern'], mean_stat)

    def nInput_datasets(self):
        return 1
    def nOutput_datasets(self):
        return 2
    def get_max_frames(self):
        return 'single'
