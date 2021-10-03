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
.. module:: reduction_amax
   :platform: Unix
   :synopsis: reducing data by one dimension by taking amax along the chosen dimension

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""

import copy
import numpy as np

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class ReductionAmax(Plugin, CpuPlugin):

    def __init__(self):
        super(ReductionAmax, self).__init__('ReductionAmax')

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()

        rm_label = self.parameters['axis_label']
        rm_dim = in_dataset[0].get_data_dimension_by_axis_label(rm_label)
        patterns = [self.parameters['pattern'] + '.' + str(rm_dim)]
        axis_labels = copy.copy(in_dataset[0].get_axis_labels())
        del axis_labels[rm_dim]

        shape = list(in_dataset[0].get_shape())
        del shape[rm_dim]

        out_dataset[0].create_dataset(
                patterns={in_dataset[0]: patterns},
                axis_labels=axis_labels,
                shape=tuple(shape))

        in_pData, out_pData = self.get_plugin_datasets()
        getall = [self.parameters['pattern'], 'label']
        in_pData[0].plugin_data_setup('VOLUME_3D', 'single', getall=getall)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def process_frames(self, data):
        reduce_dim = np.argmin(np.shape(data[0])) # get the index of smallest dimension
        result = np.amax(data[0].copy(),axis=reduce_dim)
        return result

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
