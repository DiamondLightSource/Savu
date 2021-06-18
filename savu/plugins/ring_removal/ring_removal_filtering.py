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
.. module:: ring_removal_filtering
   :platform: Unix
   :synopsis: Method working in the sinogram space to remove ring artifacts.
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from scipy.ndimage import median_filter
from scipy import signal
import pyfftw.interfaces.scipy_fftpack as fft


@register_plugin
class RingRemovalFiltering(Plugin, CpuPlugin):

    def __init__(self):
        super(RingRemovalFiltering, self).__init__(
            "RingRemovalFiltering")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()
        width_dim = \
            in_pData[0].get_data_dimension_by_axis_label('detector_x')
        height_dim = \
            in_pData[0].get_data_dimension_by_axis_label('rotation_angle')
        sino_shape = list(in_pData[0].get_shape())
        self.width1 = sino_shape[width_dim]
        self.pad = min(int(0.1 * sino_shape[height_dim]), 150)
        self.height1 = sino_shape[height_dim] + 2 * self.pad
        listindex = np.arange(0.0, sino_shape[height_dim], 1.0)
        self.matindex = np.tile(listindex, (self.width1, 1))
        sigma = np.clip(np.int16(self.parameters['sigma']), 1, self.height1 - 1)
        self.window = signal.gaussian(self.height1, std=sigma)
        self.listsign = np.power(-1.0, np.arange(self.height1))

    def remove_stripe_based_sorting(self, matindex, sinogram, size):
        """Remove stripes using the sorting technique.

        Parameters
        ---------
        sinogram : 2D array.
        size : Window size of the median filter.

        Returns
        ---------
            Stripe-removed sinogram.
        """
        sinogram = np.transpose(sinogram)
        matcomb = np.asarray(np.dstack((matindex, sinogram)))
        matsort = np.asarray(
            [row[row[:, 1].argsort()] for row in matcomb])
        matsort[:, :, 1] = median_filter(matsort[:, :, 1], (size, 1))
        matsortback = np.asarray(
            [row[row[:, 0].argsort()] for row in matsort])
        sino_corrected = matsortback[:, :, 1]
        return np.transpose(sino_corrected)

    def process_frames(self, data):
        sinogram = np.transpose(np.copy(data[0]))
        sinogram2 = np.pad(
            sinogram, ((0, 0), (self.pad, self.pad)), mode='reflect')
        size = np.clip(np.int16(self.parameters['size']), 1, self.width1 - 1)
        sinosmooth = np.zeros_like(sinogram)
        for i, sinolist in enumerate(sinogram2):
            sinosmooth[i] = np.real(fft.ifft(
                fft.fft(sinolist * self.listsign) *
                self.window) * self.listsign)[self.pad:self.height1 - self.pad]
        sinosharp = sinogram - sinosmooth
        sinosmooth_cor = np.transpose(
            self.remove_stripe_based_sorting(
                self.matindex, np.transpose(sinosmooth), size))
        return np.transpose(sinosmooth_cor + sinosharp)
