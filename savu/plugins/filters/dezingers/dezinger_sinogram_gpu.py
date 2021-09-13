# Copyright 2020 Diamond Light Source Ltd.
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
.. module:: dezinger_sinogram_gpu
   :platform: Unix
   :synopsis: A 2D/3D GPU median-based dezinger plugin to apply to sinogram data
.. moduleauthor::Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.filters.dezingers.base_dezinger_sinogram import BaseDezingerSinogram
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from larix.methods.misc_gpu import MEDIAN_DEZING_GPU

@register_plugin
class DezingerSinogramGpu(BaseDezingerSinogram, GpuPlugin):

    def __init__(self):
        super(DezingerSinogramGpu, self).__init__("DezingerSinogramGpu")
        self.GPU_index = None
        self.res = False
        self.start = 0

    def process_frames(self, data):
        input_temp = data[0]
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0
        std_dev = np.std(input_temp)
        input_temp =np.swapaxes(input_temp,0,1)        
        result = MEDIAN_DEZING_GPU(input_temp.copy(order='C'), self.parameters['kernel_size'], std_dev*self.parameters['outlier_mu'])
        return np.swapaxes(result,0,1)
