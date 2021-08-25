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
.. module:: thresh_segm
   :platform: Unix
   :synopsis: Segmentation by threhsolding based on lower and upper intensities

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np

@register_plugin
class ThreshSegm(Plugin, CpuPlugin):

    def __init__(self):
        super(ThreshSegm, self).__init__("ThreshSegm")

    def setup(self):

        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def pre_process(self):
        # extract given parameters
        self.min_limit = self.parameters['min_intensity']
        self.max_limit = self.parameters['max_intensity']
        self.value = self.parameters['value']

    def process_frames(self, data):
        thresh_result = np.uint8(np.zeros(np.shape(data[0])))
        thresh_result[(data[0] >= self.min_limit) & (data[0] < self.max_limit)] = self.value
        return thresh_result

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
