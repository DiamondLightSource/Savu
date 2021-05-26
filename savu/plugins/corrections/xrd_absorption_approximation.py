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
.. module:: xrd_absorption_approximation
   :platform: Unix
   :synopsis: A plugin apply xrd absorption approximation using stxm data
.. moduleauthor:: Stephen W.T. Price <stephen.price@diamond.ac.uk>
"""

import numpy as np
import logging
from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
import _xraylib as xl


@register_plugin
class XrdAbsorptionApproximation(BaseFilter, CpuPlugin):

    def __init__(self):
        logging.debug("Starting Xrd Absorption Approximation")
        super(XrdAbsorptionApproximation,
              self).__init__("XrdAbsorptionApproximation")

    def pre_process(self):
        compound = self.parameters['compound']
        density = self.parameters['density']
        mData = self.get_in_meta_data()[0]
        mono_energy = mData.get('mono_energy')
        peak_energy = mData.get('mono_energy')
        pump_mu = self.get_mu(compound, float(mono_energy), density)
        # sets outgoing x-ray energy to incoming x-ray energy
        peak_mu = self.get_mu(compound, float(mono_energy), density)
        logging.debug("THE PUMP MU IS is:"+str(pump_mu)+str(mono_energy))
        logging.debug("THE PEAK MU IS is:"+str(peak_mu)+str(peak_energy))

        self.atten_ratio = peak_mu/pump_mu
        theta = mData.get('rotation_angle')
        self.dtheta = theta[1]-theta[0]
        if np.abs(self.dtheta) > 10.0:
            logging.warning('Theta step is greater than 10 degrees! Watch out!')
        self.npix_displacement = \
            self.parameters['azimuthal_offset']//self.dtheta
        logging.debug('This gives a pixel offset of %s'
                      % str(self.npix_displacement))
        if self.parameters['log_me']:
            self.stxm = np.log10(np.squeeze(
                    self.exp.index['in_data']['stxm'].data[...]))
        self.stxm = np.squeeze(self.exp.index['in_data']['stxm'].data[...])

    def process_frames(self, data):
        xrd = data[0]
        stxm_orig = self.stxm
        logging.debug('the xrd shape is %s' % str(xrd.shape))
        logging.debug('the stxm shape is %s' % str(stxm_orig.shape))
        stxm = stxm_orig
        absorption = np.roll(stxm, int(self.npix_displacement), axis=0)
        corrected_xrd, corr_fac = self.correct_sino(1., xrd, absorption)
        return corrected_xrd

    def correct_sino(self, Ti_ratio, FFI0_Ti, absorption):
        trans_ave_array = np.ndarray(shape=FFI0_Ti.shape, dtype=np.float64)
        for n in range(len(absorption)):  # columns, axis=0
            row = absorption[n]
            trans_ave_array[n] = row
            for m in range(1, len(row), 1):  # row, axis=1
                # average of all absorption between pixel 0 and pixel
                # - removes t so should be mu only
                trans_ave_array[n][m] = np.average(row[m:-1])

        trans_ave_array = np.nan_to_num(trans_ave_array)
        exponent_Ti = \
            self.get_exponent_Ti_mu(Ti_ratio, absorption, trans_ave_array)

        FFI0_corrected_Ti = np.multiply(FFI0_Ti, exponent_Ti)
        return FFI0_corrected_Ti, exponent_Ti

    def get_exponent_Ti_mu(self, Ti_ratio, absorption, trans_ave_array):
        FF_Ti_xray_mu = np.multiply(trans_ave_array, Ti_ratio)
        exponent_Ti = np.add(FF_Ti_xray_mu, absorption)
        exponent_Ti = np.multiply(exponent_Ti, 1)
        if not self.parameters['log_me']:
            exponent_Ti = np.exp(exponent_Ti)
        return exponent_Ti

    def setup(self):
        logging.debug('setting up the base absorption correction')
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_meta_data = in_dataset[0].meta_data
        idx = [in_meta_data.get("mono_energy")]
        self.nChannels = len(idx)
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_num_channels())
        spectra = out_datasets[0]
        spectra.create_dataset(in_dataset[0])

        out_pData[0].plugin_data_setup('SINOGRAM', self.get_num_channels())

    def get_num_channels(self):
        return self.nChannels

    def get_azimuthal_offset(self):
        return self.parameters['azimuthal_offset']

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'

    def get_mu(self, compound, energy, density):
        '''
        returns mu for a compound for a single energy
        '''
        return (xl.CS_Total_CP(compound, energy)*density)*1e-2
