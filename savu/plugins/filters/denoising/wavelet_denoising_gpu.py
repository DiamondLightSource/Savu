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
.. module:: wavelet_denoising_gpu
   :platform: Unix
   :synopsis: GPU Wavelet 2D denoising from pypwt package (Pierre Paleo)

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin
from savu.core.iterate_plugin_group_utils import enable_iterative_loop, \
    check_if_end_plugin_in_iterate_group
import numpy as np

try:
    from pypwt import Wavelets
except ImportError:
    print('____! Wavelet package pywpt is missing, please install !____')

@register_plugin
class WaveletDenoisingGpu(Plugin, GpuPlugin):

    def __init__(self):
        super(WaveletDenoisingGpu, self).__init__('WaveletDenoisingGpu')
        self.GPU_index = None

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        if check_if_end_plugin_in_iterate_group(self.exp):
            return 2
        else:
            return 1

    def nClone_datasets(self):
        if check_if_end_plugin_in_iterate_group(self.exp):
            return 1
        else:
            return 0

    @enable_iterative_loop
    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def process_frames(self, data):
        input_data = np.nan_to_num(data[0])
        input_data[input_data > 10 ** 15] = 0.0

        # Running Wavelet Denoising
        # Compute the wavelets coefficients
        W = Wavelets(input_data, self.parameters['family_name'], self.parameters['nlevels'])
        W.forward()
        #  Do thresholding on the wavelets coefficients
        W.soft_threshold(self.parameters['threshold_level'])
        W.inverse()
        X = W.image
        return X
