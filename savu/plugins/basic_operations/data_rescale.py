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
.. module:: data_rescale
   :platform: Unix
   :synopsis: performs stretching or shrinking the data intensity levels based on skimage rescale_intensity module

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""


from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import skimage.exposure
import skimage.io
import numpy as np

@register_plugin
class DataRescale(Plugin, CpuPlugin):
    """
    The plugin performs stretching or shrinking the data intensity levels based on skimage rescale_intensity module. \
    Min-max scalars for rescaling can be passed from METADATA OR by providing as an input.
    
    :param min_value: the global minimum data value. Default: None.
    :param max_value: the global maximum data value. Default: None.
    """

    def __init__(self):
        super(DataRescale, self).__init__("DataRescale")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_XZ', 'single')
        out_pData[0].plugin_data_setup('VOLUME_XZ', 'single')

    def pre_process(self):
        data = self.get_in_datasets()[0]
        try:
            the_max = data.meta_data.get(['stats', 'max', 'pattern'])
        except KeyError:
            the_max = self.parameters['max_value']
        try:
            the_min = data.meta_data.get(['stats', 'min', 'pattern'])
        except KeyError:
            the_min = self.parameters['min_value']
        
        self._data_range = (the_min, the_max)

    def process_frames(self, data):
        if ((self._data_range[0] is not None) & (self._data_range[1] is not None)):
            # Rescale image to (0.0, 1.0) range
            resampled_image = skimage.exposure.rescale_intensity(data[0], in_range=self._data_range, out_range=(0.0, 1.0))
        else:
            resampled_image = data[0]
        return resampled_image
    
    def nInput_datasets(self):
        return 1
    
    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'
