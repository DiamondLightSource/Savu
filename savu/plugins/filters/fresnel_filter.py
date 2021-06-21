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
.. module:: fresnel_filter
   :platform: Unix
   :synopsis: A plugin for denoising or improving the contrast of reconstruction
    images.
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
import pyfftw.interfaces.scipy_fftpack as fft


@register_plugin
class FresnelFilter(Plugin, CpuPlugin):

    def __init__(self):
        super(FresnelFilter, self).__init__("FresnelFilter")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        self.pattern = self.parameters['pattern']
        if self.pattern == "PROJECTION":
            in_pData[0].plugin_data_setup(self.pattern, 'single')
            out_pData[0].plugin_data_setup(self.pattern, 'single')
        else:
            in_pData[0].plugin_data_setup('SINOGRAM', 'single')
            out_pData[0].plugin_data_setup('SINOGRAM', 'single')

    def make_window(self, height, width, ratio, pattern):
        center_hei = int(np.ceil((height - 1) * 0.5))
        center_wid = int(np.ceil((width - 1) * 0.5))
        if pattern == "PROJECTION":
            ulist = (1.0 * np.arange(0, width) - center_wid) // width
            vlist = (1.0 * np.arange(0, height) - center_hei) // height
            u, v = np.meshgrid(ulist, vlist)
            win2d = 1.0 + ratio * (u ** 2 + v ** 2)
        else:
            ulist = (1.0 * np.arange(0, width) - center_wid) // width
            win1d = 1.0 + ratio * ulist ** 2
            win2d = np.tile(win1d, (height, 1))
        return win2d

    def apply_filter(self, mat, window, pattern, pad_width):
        (nrow, ncol) = mat.shape
        if pattern == "PROJECTION":
            top_drop = 10  # To remove the time stamp at some data
            mat_pad = np.pad(mat[top_drop:], (
                (pad_width + top_drop, pad_width),
                (pad_width, pad_width)), mode="edge")
            win_pad = np.pad(window, pad_width,
                             mode="edge")
            mat_dec = fft.ifft2(
                fft.fft2(-np.log(mat_pad)) / fft.ifftshift(win_pad))
            mat_dec = np.abs(
                mat_dec[pad_width:pad_width + nrow, pad_width:pad_width + ncol])
        else:
            mat_pad = np.pad(
                -np.log(mat), ((0, 0), (pad_width, pad_width)), mode='edge')
            win_pad = np.pad(window, ((0, 0), (pad_width, pad_width)),
                             mode="edge")
            mat_fft = np.fft.fftshift(fft.fft(mat_pad), axes=1) / win_pad
            mat_dec = fft.ifft(np.fft.ifftshift(mat_fft, axes=1))
            mat_dec = np.abs(mat_dec[:, pad_width:pad_width + ncol])
        return np.float32(np.exp(-mat_dec))

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        self.data_size = inData.get_shape()
        (depth1, height1, width1) = self.data_size[:3]
        ratio = self.parameters['ratio']
        if self.pattern == "PROJECTION":
            self.window = self.make_window(height1, width1, ratio, self.pattern)
        else:
            self.window = self.make_window(depth1, width1, ratio, self.pattern)
        self.pad_width = min(150, int(0.1 * width1))

    def process_frames(self, data):
        mat_filt = self.apply_filter(
            data[0], self.window, self.pattern, self.pad_width)
        return mat_filt
