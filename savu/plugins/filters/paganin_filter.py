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
.. module:: paganin_filter
   :platform: Unix
   :synopsis: A plugin to apply the Paganin filter.

.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
import math
import logging
import numpy as np
import pyfftw.interfaces.scipy_fftpack as fft

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin, dawn_compatible


@dawn_compatible
@register_plugin
class PaganinFilter(BaseFilter, CpuPlugin):

    def __init__(self):
        logging.debug("initialising Paganin Filter")
        logging.debug("Calling super to make sure that all superclases are " +
                      " initialised")
        super(PaganinFilter, self).__init__("PaganinFilter")
        self.filtercomplex = None
        self.count = 0

    def set_filter_padding(self, in_pData, out_pData):
        in_data = self.get_in_datasets()[0]
        det_x = in_data.get_data_dimension_by_axis_label('detector_x')
        det_y = in_data.get_data_dimension_by_axis_label('detector_y')
        pad_det_y = '%s.%s' % (det_y, self.parameters['Padtopbottom'])
        pad_det_x = '%s.%s' % (det_x, self.parameters['Padleftright'])
        mode = self.parameters['Padmethod']
        pad_dict = {'pad_directions': [pad_det_x, pad_det_y], 'pad_mode': mode}
        in_pData[0].padding = pad_dict
        out_pData[0].padding = pad_dict

    def pre_process(self):
        self._setup_paganin(*self.get_plugin_in_datasets()[0].get_shape())

    def _setup_paganin(self, height, width):
        micron = 10 ** (-6)
        keV = 1000.0
        distance = self.parameters['Distance']
        energy = self.parameters['Energy'] * keV
        resolution = self.parameters['Resolution'] * micron
        wavelength = (1240.0 / energy) * 10.0 ** (-9)
        ratio = self.parameters['Ratio']

        height1 = height + 2 * self.parameters['Padtopbottom']
        width1 = width + 2 * self.parameters['Padleftright']
        centery = np.ceil(height1 / 2.0) - 1.0
        centerx = np.ceil(width1 / 2.0) - 1.0

        # Define the paganin filter
        dpx = 1.0 / (width1 * resolution)
        dpy = 1.0 / (height1 * resolution)
        pxlist = (np.arange(width1) - centerx) * dpx
        pylist = (np.arange(height1) - centery) * dpy
        pxx = np.zeros((height1, width1), dtype=np.float32)
        pxx[:, 0:width1] = pxlist
        pyy = np.zeros((height1, width1), dtype=np.float32)
        pyy[0:height1, :] = np.reshape(pylist, (height1, 1))
        pd = (pxx * pxx + pyy * pyy) * wavelength * distance * math.pi

        filter1 = 1.0 + ratio * pd
        self.filtercomplex = filter1 + filter1 * 1j

    def _paganin(self, data):
        pci1 = fft.fft2(np.float32(data))
        pci2 = fft.fftshift(pci1) / self.filtercomplex
        fpci = np.abs(fft.ifft2(pci2))
        result = -0.5 * self.parameters['Ratio'] * np.log(
            fpci + self.parameters['increment'])
        return result

    def process_frames(self, data):
        proj = np.nan_to_num(data[0])  # Noted performance
        proj[proj == 0] = 1.0
        return self._paganin(proj)

    def get_max_frames(self):
        return 'single'
