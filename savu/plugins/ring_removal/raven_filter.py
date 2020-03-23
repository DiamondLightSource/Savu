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
.. module:: raven_filter
   :platform: Unix
   :synopsis: A plugin to remove ring artefacts

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""
import logging
import numpy as np
import pyfftw
import pyfftw.interfaces.numpy_fft as fft

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.data.plugin_list import CitationInformation
from savu.plugins.utils import register_plugin


@register_plugin
class RavenFilter(BaseFilter, CpuPlugin):
    """
    Ring artefact removal method

    :u*param uvalue: To define the shape of filter, e.g. bad=10, moderate=20,\
        minor=50. Default: 20.
    :param vvalue: How many rows to be applied the filter. Default: 2.
    :param nvalue: To define the shape of filter. Default: 4.
    :param padFT: Padding for Fourier transform. Default: 20.
    """

    def __init__(self):
        logging.debug("Starting Raven Filter")
        super(RavenFilter, self).__init__("RavenFilter")
        self.count = 0

    def set_filter_padding(self, in_data, out_data):
        self.pad = self.parameters['padFT']
        # don't currently have functionality to pad top/bottom but not
        # right/left so padding everywhere for now
        in_data[0].padding = {'pad_frame_edges': self.pad}
        out_data[0].padding = {'pad_frame_edges': self.pad}

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        sino_shape = list(in_pData.get_shape())

        width1 = sino_shape[1] + 2*self.pad
        height1 = sino_shape[0] + 2*self.pad

        v0 = np.abs(self.parameters['vvalue'])
        u0 = np.abs(self.parameters['uvalue'])
        n = np.abs(self.parameters['nvalue'])
        # Create filter
        centerx = np.ceil(width1 / 2.0) - 1.0
        centery = np.int16(np.ceil(height1 / 2.0) - 1)
        self.row1 = centery - v0
        self.row2 = centery + v0+1
        listx = np.arange(width1)-centerx
        filtershape = 1.0/(1.0 + np.power(listx/u0, 2*n))
        filtershapepad2d = np.zeros((self.row2 - self.row1, filtershape.size))
        filtershapepad2d[:] = np.float64(filtershape)
        self.filtercomplex = filtershapepad2d + filtershapepad2d*1j

        a = pyfftw.n_byte_align_empty((height1, width1), 16, 'complex128')
        b = pyfftw.n_byte_align_empty((height1, width1), 16, 'complex128')
        c = pyfftw.n_byte_align_empty((height1, width1), 16, 'complex128')
        d = pyfftw.n_byte_align_empty((height1, width1), 16, 'complex128')
        self.fft_object = pyfftw.FFTW(a, b, axes=(0, 1))
        self.ifft_object = pyfftw.FFTW(c, d, axes=(0, 1),
                                       direction='FFTW_BACKWARD')

    def process_frames(self, data):
        sino = fft.fftshift(self.fft_object(data[0]))
        sino[self.row1:self.row2] = \
            sino[self.row1:self.row2] * self.filtercomplex
        sino = fft.ifftshift(sino)
        return self.ifft_object(sino).real

    def get_plugin_pattern(self):
        return 'SINOGRAM'

    def get_max_frames(self):
        return 'single'

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.description = \
            ("The ring artefact removal algorithm used in this processing \
             chain is taken from this work.")
        cite_info.bibtex = \
            ("@article{raven1998numerical,\n" +
             "title={Numerical removal of ring artifacts in \
             microtomography},\n" +
             "author={Raven, Carsten},\n" +
             "journal={Review of scientific instruments},\n" +
             "volume={69},\n" +
             "number={8},\n" +
             "pages={2978--2980},\n" +
             "year={1998},\n" +
             "publisher={AIP Publishing}\n" +
             "}")
        cite_info.endnote = \
            ("%0 Journal Article\n" +
             "%T Numerical removal of ring artifacts in microtomography\n" +
             "%A Raven, Carsten\n" +
             "%J Review of scientific instruments\n" +
             "%V 69\n" +
             "%N 8\n" +
             "%P 2978-2980\n" +
             "%@ 0034-6748\n" +
             "%D 1998\n" +
             "%I AIP Publishing")
        cite_info.doi = "doi: 10.1063/1.1149043"
        return cite_info
