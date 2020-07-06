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
.. module:: stripe removal using Wavelet-FFT approach doi: 10.1364/OE.17.008567
   :platform: Unix
   :synopsis: A plugin removes ring artefacts

.. moduleauthor: Nghia Vo.
   Adapted from  tomopy source code:
   http://tomopy.github.io/tomopy/_modules/tomopy/algorithms/preprocess/stripe_removal.html
"""

import logging
import numpy as np
import pyfftw.interfaces.numpy_fft as fft
import pywt

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class RingRemovalWaveletfft(BaseFilter, CpuPlugin):
    """
    Ring artefact removal method

    :param nvalue: Order of the the Daubechies (DB) wavelets. Default: 5
    :param sigma: Damping parameter. Larger is stronger. Default: 1.
    :param level: Wavelet decomposition level. Default: 3.
    :param padFT: Padding for Fourier transform. Default: 20.
    """

    def __init__(self):
        logging.debug("Starting ring remogal using Wavelet-FFT approach")
        super(RingRemovalWaveletfft, self).__init__("RingRemovalWaveletfft")
        self.count = 0

    def set_filter_padding(self, in_data, out_data):
        self.pad = self.parameters['padFT']
        # don't currently have functionality to pad top/bottom but not
        # right/left so padding everywhere for now
        in_data[0].padding = {'pad_frame_edges': self.pad}
        out_data[0].padding = {'pad_frame_edges': self.pad}

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        self.slice_dir = in_pData.get_slice_dimension()
        nDims = len(in_pData.get_shape())
        self.sslice = [slice(None)]*nDims
        sino_shape = list(in_pData.get_shape())
        if len(sino_shape) is 3:
            del sino_shape[self.slice_dir]

        self.width1 = sino_shape[1] + 2*self.pad
        self.height1 = sino_shape[0] + 2*self.pad

        n = np.abs(self.parameters['nvalue'])
        self.sigma = np.abs(self.parameters['sigma'])
        self.level = np.abs(self.parameters['level'])
        self.waveletname = 'db'+str(n)

    def process_frames(self, data):
        output = np.empty_like(data[0])
        nSlices = data[0].shape[self.slice_dir]
        for i in range(nSlices):
            self.sslice[self.slice_dir] = i
            sino = data[0][tuple(self.sslice)]
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
                damp = 1 - np.exp(-np.power(y_hat, 2) / (2 * np.power(self.sigma, 2)))
                fcV = np.multiply(fcV, np.transpose(np.tile(damp, (mx, 1))))

                 # Inverse FFT.
                cV[j] = np.real(np.fft.ifft2(np.fft.ifftshift(fcV)))
            # Wavelet reconstruction.
            for j in range(self.level)[::-1]:
                sino = sino[0:cH[j].shape[0], 0:cH[j].shape[1]]
                sino = pywt.idwt2((sino, (cH[j], cV[j], cD[j])), self.waveletname)
            if self.height1%2!=0:
                sino = sino[0:-1,:]
            if self.width1%2!=0:
                sino = sino[:,0:-1]
            output[self.sslice] = sino
        return output

    def get_plugin_pattern(self):
        return 'SINOGRAM'

    def get_max_frames(self):
        return 'multiple'

