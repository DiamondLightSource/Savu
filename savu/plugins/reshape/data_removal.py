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
.. module:: data_removal
   :platform: Unix
   :synopsis: Plugin to remove unwanted data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class DataRemoval(BaseFilter, CpuPlugin):

    def __init__(self):
        super(DataRemoval, self).__init__("DataRemoval")
        self.indices = None
        self.sl = None

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        in_data = self.get_in_datasets()[0]
        self.dim = self.parameters['dim']
        self.indices = self.calc_indices(in_data.get_shape()[self.dim])
        self.sl = [slice(None)]*len(in_pData.get_shape())
        self.sl[self.dim] = self.indices
        self.sl = tuple(self.sl)

        in_data.amend_axis_label_values(
            in_pData._get_data_slice_list(self.sl))

    def process_frames(self, data):
        return data[0][self.sl]

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()

        shape = list(in_dataset[0].get_shape())
        reduced_dim_shape = \
            len(self.calc_indices(shape[self.parameters['dim']]))
        shape[self.parameters['dim']] = reduced_dim_shape

        out_dataset[0].create_dataset(shape=tuple(shape),
                                      axis_labels=in_dataset[0],
                                      patterns=in_dataset[0])

        in_pData, out_pData = self.get_plugin_datasets()

        if self.parameters['pattern']:
            pattern = self.parameters['pattern']
        else:
            pattern = list(in_dataset[0].get_data_patterns().keys())[0]

        in_pData[0].plugin_data_setup(pattern, self.get_max_frames())
        out_pData[0].plugin_data_setup(pattern, self.get_max_frames())

    def calc_indices(self, orig_shape):
        indices = self.parameters['indices']
        if isinstance(indices, list):
            self.indices = np.array(indices)
        else:
            indices_list = indices.split(':')
            indices_list = [int(i) for i in indices_list]
            if len(indices_list) == 2:
                indices_list.append(1)
            self.indices = np.arange(*indices_list)
        return np.setxor1d(np.arange(orig_shape), self.indices)

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'multiple'
