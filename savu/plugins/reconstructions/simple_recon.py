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
.. module:: simple_recon
   :platform: Unix
   :synopsis: A simple implementation of a reconstruction routine for testing
       purposes

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.plugins.driver.cpu_plugin import CpuPlugin

import numpy as np

from savu.plugins.utils import register_plugin


@register_plugin
class SimpleRecon(BaseRecon, CpuPlugin):

    def __init__(self):
        super(SimpleRecon, self).__init__("SimpleRecon")

    def _filter(self, sinogram):
        ff = np.arange(sinogram.shape[0])
        ff -= sinogram.shape[0] // 2
        ff = np.abs(ff)
        fs = np.fft.fft(sinogram)
        ffs = fs*ff
        return np.fft.ifft(ffs).real

    def _back_project(self, mapping, sino_element, centre):
        mapping_array = mapping+centre
        return sino_element[mapping_array.astype('int')]

    def _mapping_array(self, shape, center, theta):
        x, y = np.meshgrid(np.arange(-center[0], shape[0] - center[0]),
                           np.arange(-center[1], shape[1] - center[1]))
        return x*np.cos(theta) - y*np.sin(theta)

    def process_frames(self, data):
        sino = data[0]
        centre_of_rotations, angles, vol_shape, init = self.get_frame_params()
        sinogram = sino[:, np.newaxis, :]
        try:
            centre = self.kwargs['centre']
        except Exception:
            centre = (vol_shape[0] // 2, vol_shape[1] // 2)

        results = []
        for j in range(sinogram.shape[1]):
            result = np.zeros(vol_shape, dtype=np.float32)
            for i in range(sinogram.shape[0]):
                theta = i*(np.pi/sinogram.shape[0])
                mapping_array = self._mapping_array(vol_shape, centre, theta)
                filt = np.zeros(sinogram.shape[2]*3, dtype=np.float32)
                filt[sinogram.shape[2]:sinogram.shape[2]*2] = \
                    self._filter(np.log(np.nan_to_num(sinogram[i, j, :])+1))
                result += \
                    self._back_project(mapping_array, filt,
                                       (centre_of_rotations +
                                           sinogram.shape[2]))
            results.append(result[:, np.newaxis, :])
        result = np.hstack(results)
        return result

    def get_max_frames(self):
        return 'single'
