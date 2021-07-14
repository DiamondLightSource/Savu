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
.. module:: mc_near_absorption_correction
   :platform: Unix
   :synopsis: A plugin apply hogans xrf absorption correction using stxm data

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import numpy as np
import logging
from savu.plugins.absorption_corrections.base_absorption_correction \
    import BaseAbsorptionCorrection
from savu.plugins.utils import register_plugin


@register_plugin
class McNearAbsorptionCorrection(BaseAbsorptionCorrection):
    """
    McNears absorption correction, takes in a normalised absorption sinogram \
    and xrf sinogram stack.

    :param in_datasets: A list of the dataset(s) to \
        process. Default: ['xrf','stxm'].
    """

    def __init__(self):
        logging.debug("Starting McNear Absorption correction")
        super(McNearAbsorptionCorrection,
              self).__init__("McNearAbsorptionCorrection")

    def pre_process(self):
        compound = self.parameters['compound']
        density = self.parameters['density']
        mData = self.get_in_meta_data()[0]

        mono_energy = mData.get('mono_energy')
        try:
            peak_energy = mData.get('PeakEnergy')
        except KeyError:
            logging.debug('No PeakEnergy: trying with the fullSpectrum')
            try:
                in_dataset, out_datasets = self.get_datasets()
                in_dataset[0].get_data_patterns()['SPECTRUM']
                peak_energy = list(mData.get('energy'))
            except KeyError:
                logging.debug("No PeakEnergy or energy axis. This won't work")
                raise

        pump_mu = self.get_mu(compound, float(mono_energy), density)
        peak_mu = self.get_mu(compound, list(peak_energy), density)
        self.atten_ratio: float = [pm / pump_mu for pm in peak_mu]

        theta = mData.get('rotation_angle')
        self.dtheta = theta[1]-theta[0]
        logging.debug('The rotation step is %s' % str(self.dtheta))
        if np.abs(self.dtheta)>10.0:
            logging.warning('The theta step is greater than 10 degrees! Watch out!')
        self.npix_displacement = self.parameters['azimuthal_offset']//self.dtheta
        logging.debug('This gives a pixel offset of %s' % str(self.npix_displacement))

    def process_frames(self, data):
        xrf = data[0]
        stxm_orig = data[1]
        logging.debug('the xrf shape is %s' % str(xrf.shape))
        logging.debug('the stxm shape is %s' % str(stxm_orig.shape))
        # take the log here, we assume it is monitor corrected already
        stxm = stxm_orig
        # now correct for the rotation offset
        absorption = np.roll(stxm,int(self.npix_displacement), axis=0)
        num_channels = self.get_num_channels()
        corrected_xrf = np.zeros_like(xrf)
        for i in range(num_channels):
            fluo_sino = xrf[:,:,i]
            corrected_xrf[:,:,i], corr_fac = self.correct_sino(self.atten_ratio[i], fluo_sino, absorption)
            logging.debug('For channel %s, min correction: %s, max correction: %s' % (str(i),
                                                                                      str(np.min(corr_fac)),
                                                                                      str(np.max(corr_fac))))
        return corrected_xrf

    def correct_sino(self,Ti_ratio, FFI0_Ti, absorption):
        trans_ave_array = np.ndarray(shape=FFI0_Ti.shape, dtype=np.float64)
        for n in range(len(absorption)): #columns, axis=0
            row = absorption[n]
            trans_ave_array[n] = row
            for m in range(1, len(row), 1): #row, axis=1
                trans_ave_array[n][m] = np.average(row[0:m]) #average of all absorption between pixel 0 and pixel - removes t so should be mu only

        trans_ave_array = np.nan_to_num(trans_ave_array)
        exponent_Ti = self.get_exponent_Ti_mu(Ti_ratio, absorption, trans_ave_array)
        FFI0_corrected_Ti = np.multiply(FFI0_Ti, exponent_Ti)
        return FFI0_corrected_Ti, exponent_Ti

    def get_exponent_Ti_mu(self, Ti_ratio, absorption, trans_ave_array):
        FF_Ti_xray_mu = np.multiply(trans_ave_array, Ti_ratio)
        exponent_Ti = np.add(FF_Ti_xray_mu, absorption)
        exponent_Ti = np.exp(exponent_Ti)
        return exponent_Ti
