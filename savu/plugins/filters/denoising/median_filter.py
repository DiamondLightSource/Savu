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
.. module:: median_filter
   :platform: Unix
   :synopsis: A plugin to apply 2D/3D median filter (CPU)

.. moduleauthor::Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.filters.denoising.base_median_filter import BaseMedianFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from larix.methods.misc import MEDIAN_FILT

@register_plugin
class MedianFilter(BaseMedianFilter, CpuPlugin):

    def __init__(self):
        super(MedianFilter, self).__init__("MedianFilter")

    def process_frames(self, data):
        input_temp = np.float32(data[0])
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0
        if (self.parameters['dimension'] == '3D'):
            if (self.parameters['pattern'] == 'VOLUME_XY'):
                input_temp =np.swapaxes(input_temp,0,2)
            if ((self.parameters['pattern'] == 'VOLUME_XZ') or (self.parameters['pattern'] == 'SINOGRAM')):
                input_temp =np.swapaxes(input_temp,0,1)
        result = MEDIAN_FILT(input_temp.copy(order='C'), self.parameters['kernel_size'])
        if (self.parameters['dimension'] == '3D'):
            if (self.parameters['pattern'] == 'VOLUME_XY'):
                result =np.swapaxes(result,0,2)
            if ((self.parameters['pattern'] == 'VOLUME_XZ') or (self.parameters['pattern'] == 'SINOGRAM')):
                result =np.swapaxes(result,0,1)
        return result

    def set_options(self, cfg):
        return cfg
