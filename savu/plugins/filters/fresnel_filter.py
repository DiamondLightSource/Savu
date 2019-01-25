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
.. module:: Improve contrast (similar to the Paganin filter)
   :platform: Unix
   :synopsis: A plugin working in sinogram space to improve the contrast\
    of the reconstruction image.
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
import numpy as np
import pyfftw.interfaces.scipy_fftpack as fft


@register_plugin
class FresnelFilter(Plugin, CpuPlugin):
    """
    Method similar to the Paganin filter working on sinogram. Used to improve
    the contrast of the reconstruction image.
    :u*param ratio: Control the strength of the filter. Greater is stronger\
    . Default: 100.0

    """

    def __init__(self):
        super(FresnelFilter, self).__init__("FresnelFilter")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()
        width_dim = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        height_dim = \
            in_pData[0].get_data_dimension_by_axis_label('rotation_angle')
        sino_shape = list(in_pData[0].get_shape())
        self.width1 = sino_shape[width_dim]
        self.height1 = sino_shape[height_dim]

    def process_frames(self, data):
        sinogram = np.copy(data[0])
        ratio = self.parameters['ratio']
        pad = 100
        ncolpad = self.width1 + 2 * pad
        centerc = np.int16(np.ceil((ncolpad - 1) * 0.5))
        ulist = 1.0 * (np.arange(0, ncolpad) - centerc) / ncolpad
        listfactor = 1.0 + ratio * ulist**2
        sinopad = np.pad(sinogram, ((0, 0), (pad, pad)), mode='edge')
        sinophase = np.zeros((self.height1, ncolpad), dtype=np.float32)
        for i in range(0, self.height1):
            sinophase[i] = np.real(fft.ifft(np.fft.ifftshift(
                np.fft.fftshift(fft.fft(sinopad[i])) / listfactor)))
        return sinophase[:, pad:ncolpad - pad]