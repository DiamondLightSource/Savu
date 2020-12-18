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
.. module:: sinogram_clean
   :platform: Unix
   :synopsis: A plugin to find the center of rotation per frame

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.driver.cpu_plugin import CpuPlugin

import math
import numpy as np
import pyfftw.interfaces.scipy_fftpack as fft

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter


@register_plugin
class SinogramClean(BaseFilter, CpuPlugin):
    """
    A plugin to calculate the centre of rotation using the Vo Method

    :param ratio: The ratio between the size of object and FOV of \
        the camera. Default: 2.0.
    :param row_drop: Drop lines around vertical center of the \
        mask. Default: 20.
    :param out_datasets: The default names. Default: [].
    """

    def __init__(self):
        super(SinogramClean, self).__init__("SinogramClean")

    def _create_mask(self, Nrow, Ncol, obj_radius):
        du = 1.0 / Ncol
        dv = (Nrow-1.0)/(Nrow*2.0*math.pi)
        cen_row = np.ceil(Nrow / 2.0)-1
        cen_col = np.ceil(Ncol / 2.0)-1
        drop = self.parameters['row_drop']
        mask = np.zeros((Nrow, Ncol), dtype=np.float32)
        for i in range(Nrow):
            num1 = np.round(((i-cen_row)*dv/obj_radius)/du)
            (p1, p2) = np.clip(np.sort((-num1+cen_col, num1+cen_col)), 0, Ncol-1)
            mask[i, p1:p2+1] = np.ones(p2-p1+1, dtype=np.float32)
        if drop < cen_row:
            mask[cen_row-drop:cen_row+drop+1, :] = np.zeros((2*drop + 1, Ncol), dtype=np.float32)
        return mask

    def process_frames(self, data):
        sino = data[0]
        sino2 = np.fliplr(sino[1:])
        (Nrow, Ncol) = sino.shape
        mask = self._create_mask(
            2*Nrow-1, Ncol, 0.5*self.parameters['ratio']*Ncol)

        FT1 = fft.fftshift(fft.fft2(np.vstack((sino, sino2))))
        sino = fft.ifft2(fft.ifftshift(FT1 - FT1*mask))
        return sino[0:Nrow].real

    def get_max_frames(self):
        return 1
