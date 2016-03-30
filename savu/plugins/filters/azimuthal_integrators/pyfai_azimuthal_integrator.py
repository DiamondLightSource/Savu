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
.. module:: pyfai_azimuthal_integrator
   :platform: Unix
   :synopsis: A plugin to integrate azimuthally "symmetric" signals i.e. SAXS,\
       WAXS or XRD.Requires a calibration file

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging
from savu.plugins.filters.base_azimuthal_integrator import \
    BaseAzimuthalIntegrator

from savu.plugins.utils import register_plugin


@register_plugin
class PyfaiAzimuthalIntegrator(BaseAzimuthalIntegrator):
    """
    1D azimuthal integrator by pyFAI
    :param use_mask: Should we mask. Default: False.
    :param num_bins: number of bins. Default: 1005.
    """

    def __init__(self):
        logging.debug("Starting 1D azimuthal integrationr")
        super(PyfaiAzimuthalIntegrator,
              self).__init__("PyfaiAzimuthalIntegrator")

    def filter_frames(self, data):
        logging.debug("Running azimuthal integration")
        mData = self.params[2]
        mask = self.params[0]
        ai = self.params[3]
        units = self.parameters['units']
        axis, remapped = ai.integrate1d(data=data[0], npt=self.npts, unit='q_nm^-1')
        axis, remapped_new = self.unit_conversion(units,axis,remapped)
        mData.set_meta_data('Q', axis) # multiplied because their units are wrong!
        return remapped_new
