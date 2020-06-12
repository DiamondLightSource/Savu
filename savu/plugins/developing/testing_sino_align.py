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
.. module:: testing_sino_align
   :platform: Unix
   :synopsis: A plugin to determine the centre of rotation of a sinogram and\
       to align the rows of a sinogram e.g. in the case of motor backlash.

.. moduleauthor:: Stephen Price

"""

import logging
from scipy import ndimage
from scipy.optimize import curve_fit
import scipy.ndimage.filters as filter
import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin
from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class TestingSinoAlign(Plugin, CpuPlugin):
    """
    The centre of mass of each row is determined and then a sine function fit
    through these to determine the centre of rotation.  The residual between\
    each centre of mass and the sine function is then used to align each row.

    :param threshold: e.g. [a, b] will set all values above a to \
        b. Default: None.
    :param p0: Initial guess for the parameters of \
        scipy.optimize.curve_fit. Default: (1, 1, 1).
    """

    def __init__(self):
        logging.debug("initialising Sinogram Alignment")
        super(TestingSinoAlign, self).__init__("TestingSinoAlign")

    def process_frames(self, data):
        """
        Should be overloaded by filter classes extending this one

        :param data: The data to filter
        :type data: ndarray
        :returns:  The filtered image
        """
        sino = data[0]
        if self.parameters['threshold']:
            a, b = self.parameters['threshold']
            sino[sino > a] = b
        com_x = \
            self.get_in_datasets()[0].meta_data.get('rotation_angle')
        com_y = self._com_y(1-sino)
        fitpars, covmat = \
            curve_fit(self._sinfunc, com_x, com_y, p0=self.parameters['p0'])
        return com_y - self._sinfunc(com_x, *fitpars)

    def _com_y(self, sinogram):
        com_y = []
        for row in sinogram:
            com = ndimage.measurements.center_of_mass(
                filter.gaussian_filter(row, sigma=1))
            com_y.append(com[0])
        return np.array(com_y)

    def _sinfunc(self, data, a, b, c):
        return (a*np.sin(np.deg2rad(data-b)))+c

    def _shift(self, sinogram, com_x, com_y):
        fitpars, covmat = \
            curve_fit(self._sinfunc, com_x, com_y, p0=self.parameters['p0'])
        variances = covmat.diagonal()
        std_devs = np.sqrt(variances)
        residual = com_y - self._sinfunc(com_x, *fitpars)
        centre_of_rotation_shift = residual
        np.array_split(sinogram, sinogram.shape[0], axis=0)
        n = 0
        shifted_sinogram = []
        for row in sinogram:
            shifted_sinogram_row = \
                ndimage.interpolation.shift(row, [centre_of_rotation_shift[n]],
                                            mode='nearest')
            shifted_sinogram.append(shifted_sinogram_row)
            n += 1
            output = np.vstack(shifted_sinogram)
        return output

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        self.orig_full_shape = in_dataset[0].get_shape()

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())

        fullData = in_dataset[0]

        slice_dirs = np.array(in_pData[0].get_slice_directions())
        # new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 1)
        new_shape = fullData.get_shape()[0:-1][::-1]

        self.orig_shape = \
            (np.prod(np.array(self.orig_full_shape)[slice_dirs]), 1)

        out_dataset[0].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'])
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))

        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())

    def get_plugin_pattern(self):
        return 'SINOGRAM'

    def get_max_frames(self):
        return 'single'

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.description = \
            ("The Tomographic filtering performed in this processing " +
             "chain is derived from this work.")
        cite_info.bibtex = \
            ("@Article{C4CP04488F, \n" +
             "author ={Price, S. W. T. and Ignatyev, K. and Geraki, K. and \
             Basham, M. and Filik, J. and Vo, N. T. and Witte, P. T. and \
             Beale, A. M. and Mosselmans, J. F. W.}, \n" +
             "title  ={Chemical imaging of single catalyst particles with \
             scanning [small mu ]-XANES-CT and [small mu ]-XRF-CT}, \n" +
             "journal  ={Phys. Chem. Chem. Phys.}, \n" +
             "year  ={2015}, \n" +
             "volume  ={17}, \n" +
             "issue  ={1}, \n" +
             "pages  ={521-529}, \n" +
             "publisher  ={The Royal Society of Chemistry}, \n" +
             "doi  ={10.1039/C4CP04488F}, \n" +
             "url  ={https://doi.org/10.1039/C4CP04488F}, \n" +
             "}")
        cite_info.endnote = \
            ("%0 Journal Article\n" +
             "%T Chemical imaging of single catalyst particles with scanning \
            [small mu ]-XANES-CT and [small mu ]-XRF-CT\n" +
             "%A Price, Stephen W.T.\n" +
             "%A Ignatyev, Konstantin\n" +
             "%A Geraki, Kalotina\n" +
             "%A Basham, Mark\n" +
             "%A Filik, Jacob\n" +
             "%A Vo, Nghia T.\n" +
             "%A Witte, Peter T.\n" +
             "%A Beale, Andrew M.\n" +
             "%A Mosselmans, J. Fred W.\n" +
             "%J Physical Chemistry Chemical Physics\n" +
             "%V 17\n" +
             "%N 1\n" +
             "%P 521-529\n" +
             "%@ 1094-4087\n" +
             "%D 2015\n" +
             "%I Royal Society of Chemistry")
        cite_info.doi = "doi: 10.1039/c4cp04488f"
        return cite_info
