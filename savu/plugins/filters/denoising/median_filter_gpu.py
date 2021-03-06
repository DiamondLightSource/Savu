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
.. module:: median filter (GPU) from the Larix software
   :platform: Unix
   :synopsis: A plugin to apply 2D/3D median filter (GPU)

.. moduleauthor::Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from larix.methods.misc_gpu import MEDIAN_FILT_GPU

@register_plugin
class MedianFilterGpu(Plugin, GpuPlugin):
    """
    A plugin to apply 2D/3D median filter on a GPU. The 3D capability is enabled\
    through padding. Note that the kernel_size in 2D will be kernel_size x kernel_size
    and in 3D case kernel_size x kernel_size x kernel_size.

    :u*param kernel_size: Kernel size of the median filter. Default: 3.
    :u*param dimension: dimensionality of the filter 2D/3D. Default: '3D'.
    :u*param pattern: pattern to apply this to. Default: "PROJECTION".
    """

    def __init__(self):
        super(MedianFilterGpu, self).__init__('MedianFilterGpu')
        self.GPU_index = None
        self.res = False
        self.start = 0

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def process_frames(self, data):
        input_temp = np.float32(data[0])
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0
        if (self.parameters['dimension'] == '3D'):
            if (self.parameters['pattern'] == 'VOLUME_XY'):
                input_temp =np.swapaxes(input_temp,0,2)
            if ((self.parameters['pattern'] == 'VOLUME_XZ') or (self.parameters['pattern'] == 'SINOGRAM')):
                input_temp =np.swapaxes(input_temp,0,1)
        result = MEDIAN_FILT_GPU(input_temp.copy(order='C'), self.parameters['kernel_size'])
        if (self.parameters['dimension'] == '3D'):
            if (self.parameters['pattern'] == 'VOLUME_XY'):
                result =np.swapaxes(result,0,2)
            if ((self.parameters['pattern'] == 'VOLUME_XZ') or (self.parameters['pattern'] == 'SINOGRAM')):
                result =np.swapaxes(result,0,1)
        return result

    def set_filter_padding(self, in_data, out_data):
        if (self.parameters['dimension'] == '3D'):
            padding = (self.parameters['kernel_size']-1)/2
        else:
            padding = 0
        in_data[0].padding = {'pad_multi_frames': padding}
        out_data[0].padding = {'pad_multi_frames': padding}

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_plugin_pattern(self):
        return self.parameters['pattern']
