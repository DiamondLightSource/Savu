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
.. module:: phase_unwrapping
   :platform: Unix
   :synopsis: A plugin for unwrapping phase-retrieved images.

.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.plugin import Plugin

import numpy as np
import pyfftw.interfaces.scipy_fftpack as fft


@register_plugin
class PhaseUnwrapping(Plugin, CpuPlugin):

    def __init__(self):
        super(PhaseUnwrapping, self).__init__("PhaseUnwrapping")

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

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

    def wrap_to_pi(self, mat):
        return (mat + np.pi) % (2 * np.pi) - np.pi

    def make_window(self, height, width):
        wid_cen = width // 2
        hei_cen = height // 2
        ulist = (1.0 * np.arange(0, width) - wid_cen) / wid_cen
        vlist = (1.0 * np.arange(0, height) - hei_cen) / hei_cen
        u, v = np.meshgrid(ulist, vlist)
        window = u ** 2 + v ** 2
        window1 = np.copy(window)
        window1[hei_cen, wid_cen] = 1.0
        return window, window1

    def forward_operator(self, mat, window):
        mat_res = fft.ifft2(fft.ifftshift(fft.fftshift(
            fft.fft2(mat)) * window))
        return mat_res

    def backward_operator(self, mat, window1):
        mat_res = fft.ifft2(fft.ifftshift(fft.fftshift(
            fft.fft2(mat)) / window1))
        return mat_res

    def double_image(self, mat):
        mat1 = np.hstack((mat, np.fliplr(mat)))
        mat2 = np.vstack((np.flipud(mat1), mat1))
        return mat2

    def phase_unwrap_based_fft(self, mat, window, window1):
        height, width = mat.shape
        mat2 = self.double_image(mat)
        mat_unwrap = np.real(
            self.backward_operator(np.imag(self.forward_operator(
                np.exp(mat2 * 1j), window) * np.exp(-1j * mat2)), window1))
        mat_unwrap = mat_unwrap[height:, 0:width]
        return mat_unwrap

    def phase_unwrap_iterative(self, mat_wrap, window, window1, n_iter):
        mat_unwrap = self.phase_unwrap_based_fft(mat_wrap, window, window1)
        for i in range(n_iter):
            mat_wrap1 = self.wrap_to_pi(mat_unwrap)
            mat_diff = mat_wrap - mat_wrap1
            nmean = np.mean(mat_diff)
            mat_diff = self.wrap_to_pi(mat_diff - nmean)
            phase_diff = self.phase_unwrap_based_fft(mat_diff, window,
                                                     window1)
            mat_unwrap = mat_unwrap + phase_diff
        return mat_unwrap

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        self.data_size = inData.get_shape()
        (self.depth, self.height, self.width) = self.data_size[:3]
        if self.pattern == "PROJECTION":
            self.window, self.window1 = self.make_window(2 * self.height,
                                                         2 * self.width)
        else:
            self.window, self.window1 = self.make_window(2 * self.depth,
                                                         2 * self.width)

        self.n_iter = self.parameters['n_iterations']

    def process_frames(self, data):
        mat_unwrap = self.phase_unwrap_iterative(data[0], self.window,
                                                 self.window1, self.n_iter)
        return mat_unwrap
