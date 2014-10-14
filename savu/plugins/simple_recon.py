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
   :synopsis: A simple implementation a reconstruction routine for testing
       purposes

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.base_recon import BaseRecon
from savu.data.process_data import CitationInfomration
from savu.plugins.cpu_plugin import CpuPlugin

import numpy as np


class SimpleRecon(BaseRecon, CpuPlugin):
    """
    A Plugin to apply a simple reconstruction with no dependancies
    """

    def __init__(self):
        super(SimpleRecon, self).__init__("SimpleRecon")

    def _filter(self, sinogram):
        ff = np.arange(sinogram.shape[0])
        ff -= sinogram.shape[0]/2
        ff = np.abs(ff)
        fs = np.fft.fft(sinogram)
        ffs = fs*ff
        return np.fft.ifft(ffs).real

    def _back_project(self, mapping, sino_element, center):
        mapping_array = mapping+center
        return sino_element[mapping_array.astype('int')]

    def _mapping_array(self, shape, center, theta):
        x, y = np.meshgrid(np.arange(-center[0], shape[0] - center[0]),
                           np.arange(-center[1], shape[1]-center[1]))
        return x*np.cos(theta) - y*np.sin(theta)

    def reconstruct(self, sinogram, centre_of_rotation, angles, shape, center):
        result = np.zeros(shape)
        sino = np.nan_to_num(sinogram)
        sino = np.log(sino+1)
        for i in range(sinogram.shape[0]):
            theta = i * (np.pi/sinogram.shape[0])
            mapping_array = self._mapping_array(shape, center, theta)
            filt = np.zeros(sinogram.shape[1]*3)
            filt[sinogram.shape[1]:sinogram.shape[1]*2] = \
                self._filter(sino[i, :])
            result += \
                self._back_project(mapping_array, filt,
                                   (centre_of_rotation + sinogram.shape[1]))
        return result

    def get_citation_inforamtion(self):
        cite_info = CitationInfomration()
        cite_info.description = \
            ("The Tomographic reconstruction performed in this processing " +
             "chain is derived from this work.")
        cite_info.bibtex = \
            ("@book{avinash2001principles,\n" +
             "  title={Principles of computerized tomographic imaging},\n" +
             "  author={Avinash C.. Kak and Slaney, Malcolm},\n" +
             "  year={2001},\n" +
             "  publisher={Society for Industrial and Applied Mathematics}\n" +
             "}")
        cite_info.endnote = \
            ("%0 Book\n" +
             "%T Principles of computerized tomographic imaging\n" +
             "%A Avinash C.. Kak\n" +
             "%A Slaney, Malcolm\n" +
             "%@ 089871494X\n" +
             "%D 2001\n" +
             "%I Society for Industrial and Applied Mathematics")
        cite_info.doi = "http://dx.doi.org/10.1137/1.9780898719277"
        return cite_info
