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
.. module:: a dezinger filter (based on the median) from the Larix software
   :platform: Unix
   :synopsis: A 2D/3D median-based dezinger plugin to apply to any data
.. moduleauthor::Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from larix.methods.misc import MEDIAN_DEZING

@register_plugin
class DezingerLarix(Plugin, CpuPlugin):
    """
    A plugin to apply 2D/3D median-based dezinger. The 3D capability is enabled\
    through padding. Note that the kernel_size in 2D will be kernel_size x kernel_size
    and in 3D case kernel_size x kernel_size x kernel_size.
    
    :u*param kernel_size: Kernel size of the median filter. Default: 3.
    :param outlier_mu: Threshold for detecting outliers, greater is less \
    sensitive. If very small, dezinger acts like a median filter. Default: 1.0.
    :u*param dimension: dimensionality of the filter 2D/3D. Default: '3D'.
    :u*param pattern: pattern to apply this to. Default: "PROJECTION".
    """

    def __init__(self):
        super(DezingerLarix, self).__init__("DezingerLarix")

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
        result = MEDIAN_DEZING(input_temp.copy(order='C'), self.parameters['kernel_size'], self.parameters['outlier_mu'])
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
