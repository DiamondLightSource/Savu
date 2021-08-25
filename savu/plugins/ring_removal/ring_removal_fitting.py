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
.. module:: ring_removal_fitting
   :platform: Unix
   :synopsis: Method working in the sinogram space to remove ring artifacts.
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
import pyfftw.interfaces.scipy_fftpack as fft
from scipy.signal import savgol_filter


@register_plugin
class RingRemovalFitting(Plugin, CpuPlugin):

    def __init__(self):
        super(RingRemovalFitting, self).__init__(
            "RingRemovalFitting")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')

    def _create_2d_window(self, height, width, sigmax, sigmay):
        """Create a 2D Gaussian window.

        Parameters
        -----------
        height, width : shape of the window.
        sigmax, sigmay : sigmas of the window.

        Returns
        ---------
            2D array.
        """
        centerx = (width - 1.0) / 2.0
        centery = (height - 1.0) / 2.0
        y, x = np.ogrid[-centery:height - centery, -centerx:width - centerx]
        numx = 2.0 * sigmax * sigmax
        numy = 2.0 * sigmay * sigmay
        win2d = np.exp(-(x * x / numx + y * y / numy))
        return win2d

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()
        width_dim = \
            in_pData[0].get_data_dimension_by_axis_label('detector_x')
        height_dim = \
            in_pData[0].get_data_dimension_by_axis_label('rotation_angle')
        sino_shape = list(in_pData[0].get_shape())
        self.pad = min(int(0.1 * sino_shape[height_dim]), 50)
        self.width1 = sino_shape[width_dim] + 2 * self.pad
        self.height1 = sino_shape[height_dim] + 2 * self.pad
        sigmax = np.clip(np.int16(
            self.parameters['sigmax']), 1, self.width1 - 1)
        sigmay = np.clip(np.int16(
            self.parameters['sigmay']), 1, self.height1 - 1)
        self.window2d = self._create_2d_window(
            self.height1, self.width1, sigmax, sigmay)
        self.order = np.clip(
            np.int16(self.parameters['order']), 0, self.height1 - 1)
        listx = np.arange(0, self.width1)
        listy = np.arange(0, self.height1)
        x, y = np.meshgrid(listx, listy)
        self.matsign = np.power(-1.0, x + y)

    def process_frames(self, data):
        sinogram = data[0]
        (height, _) = sinogram.shape
        if height % 2 == 0:
            height = height - 1
        sinofit = np.abs(savgol_filter(
            sinogram, height, self.order, axis=0, mode='mirror'))
        sinofit2 = np.pad(
            sinofit, ((0, 0), (self.pad, self.pad)), mode='edge')
        sinofit2 = np.pad(
            sinofit2, ((self.pad, self.pad), (0, 0)), mode='mean')
        sinofitsmooth = np.real(fft.ifft2(fft.fft2(
            sinofit2 * self.matsign) * self.window2d) * self.matsign)
        sinofitsmooth = sinofitsmooth[self.pad:self.height1 - self.pad,
                        self.pad:self.width1 - self.pad]
        num1 = np.mean(sinofit)
        num2 = np.mean(sinofitsmooth)
        sinofitsmooth = num1 * sinofitsmooth / num2
        return sinogram / sinofit * sinofitsmooth
