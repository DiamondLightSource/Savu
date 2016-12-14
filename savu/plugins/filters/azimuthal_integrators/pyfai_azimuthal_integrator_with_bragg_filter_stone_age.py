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
.. module:: pyfai_azimuthal_integrator_with_bragg_filter
   :platform: Unix
   :synopsis: A plugin to integrate azimuthally "symmetric" signals i.e. SAXS, WAXS or XRD.Requires a calibration file
.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging
import numpy as np
import math
from savu.plugins.filters.base_azimuthal_integrator import BaseAzimuthalIntegrator
from savu.plugins.utils import register_plugin
from scipy.interpolate import interp1d
from pyFAI import units, AzimuthalIntegrator
import time
from copy import deepcopy
@register_plugin
class PyfaiAzimuthalIntegratorWithBraggFilterStoneAge(BaseAzimuthalIntegrator):
    """
    Uses pyfai to remap the data We then remap percentile file and integrate.
    :param use_mask: Should we mask. Default: False.
    :param num_bins: number of bins. Default: 1005.
    :param thresh: threshold of percentile filter. Default: 50.
    :param offset: constant. Default: 990.0.
    """
    def __init__(self):
        logging.debug("Starting 1D azimuthal integrationr")
        super(PyfaiAzimuthalIntegratorWithBraggFilterStoneAge,
              self).__init__("PyfaiAzimuthalIntegratorWithBraggFilterStoneAge")

    def pre_process(self):
        in_dataset, out_datasets = self.get_datasets()
        mData = self.get_in_meta_data()[0]
        in_d1 = in_dataset[0]
        ai = AzimuthalIntegrator()  # get me an integrator object
        # prep the goemtry
        px_m = mData.get_meta_data('x_pixel_size')
        bc_m = [mData.get_meta_data("beam_center_x"),
              mData.get_meta_data("beam_center_y")] # in metres
        bc = bc_m /px_m # convert to pixels
        px = px_m*1e6 # convert to microns
        distance = mData.get_meta_data('distance')*1e3 # convert to mm
        wl = mData.get_meta_data('incident_wavelength')[...]# in m
        self.wl = wl
        
        yaw = -mData.get_meta_data("yaw")
        roll = mData.get_meta_data("roll")
        self.ai_params = distance, bc[0], bc[1], yaw, roll, px, px
        ai.setFit2D(distance, bc[0], bc[1], yaw, roll, px, px, None)
        ai.set_wavelength(wl)
        logging.debug(ai)

        self.sh = in_d1.get_shape()[-2:]
        self.npts = self.get_parameters('num_bins')
        foo = units.to_unit(units.TTH) #  preallocate
        pretenddata = np.zeros(self.sh)
        pretendfit = ai.integrate1d(data=pretenddata, npt=self.npts, unit='q_A^-1', correctSolidAngle=False)
        self.add_axes_to_meta_data(pretendfit[0],mData)
        twotheta=ai.__getattribute__(foo.center)(self.sh) # get the detector array of Q # preallocate
        twotheta *= 180.0/np.pi # preallocate
        twotheta_flat = twotheta.ravel() #pre allocate
        self.params = [self.npts, mData, twotheta_flat]
#         self.params = [self.npts, mData, ai, twotheta_flat]

    def filter_frames(self, data):
        print '############ ONE FILTER FRAME ########################'
        bc = [0,0]
        distance, bc[0], bc[1], yaw, roll, px, px = self.ai_params
        t1 = time.time()
        data = data[0].astype(np.float)
        data -= np.min(data)
        mData = self.params[1]
#         print self.params[2]
#         foo = self.params[2]
        
        ai = AzimuthalIntegrator()
        ai.setFit2D(distance, bc[0], bc[1], yaw, roll, px, px, None)
        ai.set_wavelength(self.wl)
        foo = units.to_unit(units.TTH)
        twotheta=ai.__getattribute__(foo.center)(self.sh) # get the detector array of Q # preallocate
        twotheta *= 180.0/np.pi # preallocate
        twotheta_flat = twotheta.ravel() #pre allocate
        logging.debug(ai)
#         twotheta_flat = self.params[3]
        logging.debug("Running azimuthal integration")
        mask = np.zeros_like(data,np.int)
        fit = ai.integrate1d(data=data, npt=self.npts,unit='q_A^-1', correctSolidAngle=False)
        print "here"
        mData.set_meta_data('Q', fit[0])
        newplot = self.calcfrom1d(fit[0], fit[1], twotheta_flat)
        rat = data/newplot
        thing = data.copy()
        thing[np.abs(rat-1.0) > self.parameters['thresh']*1e-2] = 0.0
        
        mask[thing == 0] = 1
#         mask[data < minval] = 0
        #mask[data > maxval] = 0
#         final = ai.integrate1d(data=data, npt=self.npts,unit='q_A^-1', correctSolidAngle=False)# works...
        del ai

        ai = AzimuthalIntegrator()
        ai.setFit2D(distance, bc[0], bc[1], yaw, roll, px, px, None)
        ai.set_wavelength(self.wl)
        print "DATA.shape is %s " % str(data.shape)


        final = ai.integrate1d(data, self.npts, mask=mask,unit='q_A^-1', correctSolidAngle=False, method='numpy')# doesn't work
#         final = ai.integrate1d(data=data, npt=self.npts,mask=mask,unit='q_A^-1', correctSolidAngle=False)# doesn't work
        t2 = time.time()
        del ai
#         print final[1].shape
        print "PyFAI iteration with correction took:"+str((t2-t1)*1e3)+"ms"
        print '##################END##################'
        return final[1]

    def calcfrom1d(self, tth, I, twotheta_flat):
        '''
        takes the 1D data and makes it two d again
        tth is the two theta from the integrator
        I is the intensity from the integrator
         ai is the integrator object
        '''
        interpedvals = np.interp(twotheta_flat, tth, I)
        new_image = interpedvals.reshape(self.sh)
        return new_image 
