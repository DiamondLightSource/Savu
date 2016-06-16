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
   :synopsis: A plugin to apply the Paganin filter

.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

import numpy as np
import math

from savu.plugins.utils import register_plugin


@register_plugin
class PaganinFilter(BaseFilter, CpuPlugin):
    """
    A plugin to apply Paganin filter (contrast enhancement) on projections

    :param Energy: Given X-ray energy in keV. Default: 53.0.
    :param Distance: Distance from sample to detection - Unit is metre. Default: 1.0.
    :param Resolution: Pixel size - Unit is micron. Default: 1.28.
    :param Ratio: ratio of delta/beta. Default: 10.0.
    :param Padtopbottom: Pad to the top and bottom of projection. Default: 10.
    :param Padleftright: Pad to the left and right of projection. Default: 10.
    :param Padmethod: Method of padding. Default: 'edge'.
    """

    def __init__(self):
        logging.debug("initialising Paganin Filter")
        logging.debug("Calling super to make sure that all superclases are " +
                      " initialised")
        super(PaganinFilter, self).__init__("PaganinFilter")
        self.filtercomplex = None
        self.count = 0

    def pre_process(self):
        pData = self.get_plugin_in_datasets()[0]
        self.slice_dir = pData.get_slice_dimension()
        nDims = len(pData.get_shape())
        self.sslice = [slice(None)]*nDims
        core_shape = list(pData.get_shape())
        del core_shape[self.slice_dir]
        self._setup_paganin(*core_shape)

    def _setup_paganin(self, height, width):
        micron = 10**(-6)
        keV = 1000.0
        distance = self.parameters['Distance']
        energy = self.parameters['Energy']*keV
        resolution = self.parameters['Resolution']*micron
        wavelength = (1240.0/energy)*10.0**(-9)
        ratio = self.parameters['Ratio']
        padtopbottom = self.parameters['Padtopbottom']
        padleftright = self.parameters['Padleftright']
        height1 = height + 2*padtopbottom
        width1 = width + 2*padleftright
        centery = np.ceil(height1/2.0)-1.0
        centerx = np.ceil(width1/2.0)-1.0
        # Define the paganin filter
        dpx = 1.0/(width1*resolution)
        dpy = 1.0/(height1*resolution)
        pxlist = (np.arange(width1)-centerx)*dpx
        pylist = (np.arange(height1)-centery)*dpy
        pxx = np.zeros((height1, width1), dtype=np.float32)
        pxx[:, 0:width1] = pxlist
        pyy = np.zeros((height1, width1), dtype=np.float32)
        pyy[0:height1, :] = np.reshape(pylist, (height1, 1))
        pd = (pxx*pxx+pyy*pyy)*wavelength*distance*math.pi
        filter1 = 1.0+ratio*pd
        self.filtercomplex = filter1+filter1*1j

    def _paganin(self, data, axes):
        pci1 = np.fft.fft2(np.float32(data))
        pci2 = np.fft.fftshift(pci1)/self.filtercomplex
        fpci = np.abs(np.fft.ifft2(pci2))
        result = -0.5*self.parameters['Ratio']*np.log(fpci+1.0)
        return result

    def filter_frames(self, data):
        output = np.empty_like(data[0])
        nSlices = data[0].shape[self.slice_dir]
        for i in range(nSlices):
            self.sslice[self.slice_dir] = i
            proj = data[0][tuple(self.sslice)]
            if (self.count % 100 == 0):
                logging.debug("... %i" % self.count)
            self.count += 1
            height, width = proj.shape
            proj = np.nan_to_num(proj)  # Noted performance
            proj[proj == 0] = 1.0
            padtopbottom = self.parameters['Padtopbottom']
            padleftright = self.parameters['Padleftright']
            padmethod = str(self.parameters['Padmethod'])
            proj = np.lib.pad(proj, (tuple([padtopbottom]*2),
                                     tuple([padleftright]*2)), padmethod)
            result = np.abs(np.apply_over_axes(self._paganin, proj, 0))
            output[self.sslice] = result[padtopbottom:-padtopbottom,
                                         padleftright:-padleftright]
        return output

    def get_max_frames(self):
        return 16

# TODO Add the citation information here
