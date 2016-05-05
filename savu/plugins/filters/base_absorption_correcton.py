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
.. module:: base_absorption_correction
   :platform: Unix
   :synopsis: A set of plugins to correct for absorption effects in xrd and xrf ct

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging
import numpy as np
from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from scipy.interpolate import interp1d
import _xraylib as xl


class BaseAbsorptionCorrection(BaseFilter, CpuPlugin):
    """
    a base absorption correction for stxm and xrd
    :param azimuthal_offset: angle between detectors. Default: 90.0.
    :param density: the density. Default: 3.5377.
    :param compound: the compount. Default: 'Co0.1Re0.01Ti0.05(SiO2)0.84'.
    
    """

    def __init__(self, name):
        logging.debug("Starting Absorption correction")
        super(BaseAbsorptionCorrection,
              self).__init__(name)

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_meta_data = in_dataset[0].meta_data
        idx = in_meta_data.get_meta_data("PeakIndex")
        self.nChannels = len(idx) 
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_num_channels())
        in_pData[1].plugin_data_setup('SINOGRAM', 1.0)
        spectra = out_datasets[0]
        spectra.create_dataset(in_dataset[0])

        out_pData[0].plugin_data_setup('SINOGRAM', self.get_num_channels())

    def get_num_channels(self):
        return self.nChannels

    def get_azimuthal_offset(self):
        return self.parameters['azimuthal_offset']

    def nInput_datasets(self):
        return 2

    def nOutput_datasets(self):
        return 1

    def get_mu(self, compound, energy, density):
        '''
        returns mu for a compound for a single, or list, of energies
        '''
        if isinstance(energy, (list)):
            op = []
            for e in energy:
                op.append((xl.CS_Total_CP(compound, e)*density)*1e2)
            return op
        else:
            return (xl.CS_Total_CP(compound, energy)*density)*1e2