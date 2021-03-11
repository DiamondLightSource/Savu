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
   :synopsis: A plugin to integrate azimuthally "symmetric" signals i.e. SAXS,\
       WAXS or XRD.Requires a calibration file.

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging
import numpy as np
from savu.plugins.azimuthal_integrators.base_azimuthal_integrator \
    import BaseAzimuthalIntegrator
from savu.plugins.utils import register_plugin


@register_plugin
class PyfaiAzimuthalIntegratorWithBraggFilter(BaseAzimuthalIntegrator):

    def __init__(self):
        logging.debug("Starting 1D azimuthal integration***")
        super(PyfaiAzimuthalIntegratorWithBraggFilter,
              self).__init__("PyfaiAzimuthalIntegratorWithBraggFilter")

    def process_frames(self, data):
        mData = self.params[2]
        ai = self.params[3]

        lims = self.parameters['thresh']
        num_bins_azim = self.parameters['num_bins_azim']
        num_bins_rad = self.parameters['num_bins']

        remapped, axis, _chi = \
            ai.integrate2d(data=data[0], npt_rad=num_bins_rad,
                           npt_azim=num_bins_azim, unit='q_A^-1')

        mask = np.ones_like(remapped)
        mask[remapped==0] = 0
        out = np.zeros(mask.shape[1])
        for i in range(mask.shape[1]):
#             print i
            idx = mask[:,i] == 1
            if np.sum(idx*1)==0:
                logging.warning("Found a bin where all the pixels are masked! Bin num: %s" , str(i))
                out[i] = 0.0
            else:
                foo = remapped[:,i][idx]
#                 print "the shape here is:"+str(foo.shape)
                top = np.percentile(foo,lims[1])
                bottom = np.percentile(foo,lims[0])
                out[i] = np.mean(np.clip(foo,bottom,top))
        return out
