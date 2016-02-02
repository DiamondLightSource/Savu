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
.. module:: radial integration using pyFAI
   :platform: Unix
   :synopsis: A plugin to integrate azimuthally "symmetric" signals i.e. SAXS, WAXS or XRD.Requires a calibration file

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging

import math


from pyFAI import units, AzimuthalIntegrator

import numpy as np
from savu.plugins.filters.base_azimuthal_integrator import BaseAzimuthalIntegrator

from savu.plugins.utils import register_plugin
import time


@register_plugin
class PyfaiAzimuthalIntegratorWithBraggFilter(BaseAzimuthalIntegrator):
    """
    1D azimuthal integrator by pyFAI

    :param use_mask: Should we mask. Default: False.
    :param num_bins: number of bins. Default: 1005.
    :param thresh: threshold of percentile filter. Default: 50.
    """

    def __init__(self):
        logging.debug("Starting 1D azimuthal integrationr")
        super(PyfaiAzimuthalIntegratorWithBraggFilter,
              self).__init__("PyfaiAzimuthalIntegratorWithBraggFilter")

    def pre_process(self):
        """
        This method is called after the plugin has been created by the
        pipeline framework as a pre-processing step

        :param parameters: A dictionary of the parameters for this plugin, or
            None if no customisation is required
        :type parameters: dict
        """
        in_dataset, out_datasets = self.get_datasets()
        mData = self.get_in_meta_data()[0]
        in_d1 = in_dataset[0]
        ai = AzimuthalIntegrator()  # get me an integrator object
        ### prep the goemtry
        bc = [mData.get_meta_data("beam_center_x")[...],
              mData.get_meta_data("beam_center_y")[...]]
        distance = mData.get_meta_data('distance')[...]
        wl = mData.get_meta_data('incident_wavelength')[...]
        px = mData.get_meta_data('x_pixel_size')[...]
        orien = mData.get_meta_data(
            'detector_orientation')[...].reshape((3, 3))
        #Transform
        yaw = math.degrees(-math.atan2(orien[2, 0], orien[2, 2]))
        roll = math.degrees(-math.atan2(orien[0, 1], orien[1, 1]))
        ai.setFit2D(distance, bc[0], bc[1], -yaw, roll, px, px, None)
        ai.set_wavelength(wl)
        
        self.sh = in_d1.get_shape()[-2:]
        self.npts = self.get_parameters('num_bins')
        foo = units.to_unit(units.TTH) #  preallocate
        pretenddata = np.zeros(self.sh)
        pretendfit = ai.xrpd(data=pretenddata, npt=self.npts)
        twotheta=ai.__getattribute__(foo.center)(ai.detector.max_shape) # get the detector array of Q # preallocate
        twotheta *= 180.0/np.pi # preallocate
        twotheta_flat = twotheta.ravel() #pre allocate
        self.params = [self.npts, mData, ai, twotheta_flat]
        
    def filter_frames(self, data):
        t1 = time.time()
        data = np.squeeze(data)
        mData = self.params[1]
        ai = self.params[2]
        twotheta_flat = self.params[3]
        logging.debug("Running azimuthal integration")
        fit = ai.xrpd(data=data, npt=self.npts)
        mData.set_meta_data('Q', fit[0])
        newplot = self.calcfrom1d(fit[0], fit[1], twotheta_flat)
        rat = data/newplot
        thing = data.copy()
        thing[rat > 1.000000000001] = 0.0
#         ave_per_ring = self.calcfrom1d(fit[0], fit[1], twotheta_flat)
#         thresh = self.parameters['thresh']
#         diff = (100 - thresh) / 2.0
#         minval, maxval = np.percentile(data, [diff, 100 - diff])

        mask = np.zeros_like(data)
        mask[thing == 0] = 1
#         mask[data < minval] = 0
#         mask[data > maxval] = 0
        final = ai.xrpd(data, self.npts, mask=mask)
        t2 = time.time()
        print final[1].shape
        print "PyFAI iteration with correction took:"+str((t2-t1)*1e3)+"ms"
        return final[1]




