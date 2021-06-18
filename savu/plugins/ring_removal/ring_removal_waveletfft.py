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
.. module:: ring_removal_wavelengtfft
   :platform: Unix
   :synopsis: Method working in the sinogram space to remove ring artifacts.
.. moduleauthor: Adapted from  tomopy source code:
   http://tomopy.github.io/tomopy/_modules/tomopy/algorithms/preprocess/stripe_removal.html
"""

import logging
import numpy as np
import pywt

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class RingRemovalWaveletfft(BaseFilter, CpuPlugin):

    def __init__(self):
        super(RingRemovalWaveletfft, self).__init__("RingRemovalWaveletfft")
        self.count = 0

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        self.slice_dir = in_pData.get_slice_dimension()
        nDims = len(in_pData.get_shape())
        self.sslice = [slice(None)] * nDims
        sino_shape = list(in_pData.get_shape())
        if len(sino_shape) == 3:
            del sino_shape[self.slice_dir]

        self.pad = self.parameters['padFT']
        n = np.abs(self.parameters['nvalue'])
        self.sigma = np.abs(self.parameters['sigma'])
        self.level = np.abs(self.parameters['level'])
        self.waveletname = 'db' + str(n)

    def process_frames(self, data):
        output = np.empty_like(data[0])
        nSlices = data[0].shape[self.slice_dir]
        for i in range(nSlices):
            self.sslice[self.slice_dir] = i
            sino = data[0][tuple(self.sslice)]
            (nrow, ncol) = sino.shape
            if self.pad > 0:
                sino = np.pad(sino, ((self.pad, self.pad), (0, 0)), mode='mean')
                sino = np.pad(sino, ((0, 0), (self.pad, self.pad)), mode='edge')
            # Wavelet decomposition.
            cH = []
            cV = []
            cD = []
            for j in range(self.level):
                sino, (cHt, cVt, cDt) = pywt.dwt2(sino, self.waveletname)
                cH.append(cHt)
                cV.append(cVt)
                cD.append(cDt)
            # FFT transform of horizontal frequency bands.
            for j in range(self.level):
                # FFT
                fcV = np.fft.fftshift(np.fft.fft2(cV[j]))
                my, mx = fcV.shape
                # Damping of ring artifact information.
                y_hat = (np.arange(-my, my, 2, dtype='float') + 1) / 2.0
                damp = 1 - np.exp(
                    -np.power(y_hat, 2) / (2 * np.power(self.sigma, 2)))
                fcV = np.multiply(fcV, np.transpose(np.tile(damp, (mx, 1))))
                # Inverse FFT.
                cV[j] = np.real(np.fft.ifft2(np.fft.ifftshift(fcV)))
            # Wavelet reconstruction.
            for j in range(self.level)[::-1]:
                sino = sino[0:cH[j].shape[0], 0:cH[j].shape[1]]
                sino = pywt.idwt2((sino, (cH[j], cV[j], cD[j])),
                                  self.waveletname)
            output[tuple(self.sslice)] = sino[self.pad:nrow + self.pad,
                                         self.pad:ncol + self.pad]
        return output

    def get_plugin_pattern(self):
        return 'SINOGRAM'

    def get_max_frames(self):
        return 'multiple'
