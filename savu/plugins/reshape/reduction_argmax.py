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
.. module:: reduction_argmax
   :platform: Unix
   :synopsis: reducing data by one dimension by taking argmax along the dimension

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""

import copy
import numpy as np

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class ReductionArgmax(Plugin, CpuPlugin):

    def __init__(self):
        super(ReductionArgmax, self).__init__('ReductionArgmax')

    """
    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        self.sum_dim = in_pData.get_data_dimension_by_axis_label('voxel_x')
    """

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        #print(in_dataset[0].get_data_patterns())

        #rm_label = self.parameters['axis_label']
        rm_label = 'label'
        rm_dim = in_dataset[0].get_data_dimension_by_axis_label(rm_label)
        patterns = ['VOLUME_XZ.' + str(rm_dim)]

        axis_labels = copy.copy(in_dataset[0].get_axis_labels())
        del axis_labels[rm_dim]

        shape = list(in_dataset[0].get_shape())
        del shape[rm_dim]

        out_dataset[0].create_dataset(
                patterns={in_dataset[0]: patterns},
                axis_labels=axis_labels,
                shape=tuple(shape))

        pattern = self.parameters['pattern']
        in_pData, out_pData = self.get_plugin_datasets()
        getall = ['VOLUME_XZ', 'label']
        in_pData[0].plugin_data_setup('VOLUME_3D', 'single', getall=getall)
        #in_pData[0].plugin_data_setup('VOLUME_XY', 'single')
        out_pData[0].plugin_data_setup(pattern, 'single')

    def process_frames(self, data):
        input_data = data[0]
        max_prob = np.amax(input_data,axis=2)
        print(np.shape(max_prob))
        #result = data[0].copy()
        pass

    def post_process(self):
        pass

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
