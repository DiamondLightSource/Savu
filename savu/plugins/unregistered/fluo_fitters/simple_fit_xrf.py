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
.. module:: simple_fit_xrf
   :platform: Unix
   :synopsis: A plugin to fit peaks

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
from savu.plugins.utils import register_plugin
from savu.plugins.unregistered.fluo_fitters.base_fluo_fitter \
    import BaseFluoFitter
import numpy as np
from scipy.optimize import leastsq
import time


#@register_plugin
class SimpleFitXrf(BaseFluoFitter):
    def __init__(self):
        super(SimpleFitXrf, self).__init__("SimpleFitXrf")

    def process_frames(self, data):
        t1 = time.time()
        data = data[0].squeeze()
        in_meta_data = self.get_in_meta_data()[0]
        axis = self.axis
        idx = in_meta_data.get("PeakIndex")
        positions = axis[idx]
        weights = data[idx]
        widths = np.ones_like(positions)*self.parameters["width_guess"]
        p = []
        p.extend(weights)
        p.extend(widths)
        curvetype = self.getFitFunction(str(self.parameters['peak_shape']))
        lsq1 = leastsq(self._resid, p,
                       args=(curvetype, data, axis, positions),
                       Dfun=self.dfunc, col_deriv=1)
        params = lsq1[0]
        logging.debug("done one")
        if np.isnan(params).any():
            logging.debug('Nans were detected here')
            params = np.zeros(len(params))
        weights, widths, areas = self.getAreas(curvetype,
                                               axis, positions, params)
#         areas/=np.sum(data)
#         areas /= 0.
        weights[weights<-1e-8]=0
        areas[weights < 1e-4] = 0.0
        areas[widths > 0.5] = 0.0
#         areas /= np.sum(data)
        residuals = self._resid(params, curvetype, data, axis, positions)
        t2 = time.time()
        logging.debug("Simple fit iteration took: %s ms", str((t2-t1)*1e3))
        # all fitting routines will output the same format.
        # nchannels long, with 3 elements. Each can be a subarray.
        return [weights, widths, areas, residuals]
