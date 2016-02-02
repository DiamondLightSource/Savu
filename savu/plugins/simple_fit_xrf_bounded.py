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
.. module:: simple_fit
   :platform: Unix
   :synopsis: A plugin to fit peaks

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.utils import register_plugin
from savu.plugins.base_fluo_fitter import BaseFluoFitter
import numpy as np
from scipy.optimize import leastsq , minimize


@register_plugin
class SimpleFitXrfBounded(BaseFluoFitter):
    """
    This plugin fits XRF peaks.
    :param width_guess: An initial guess at the width. Default: 0.02.

    """

    def __init__(self):
        super(SimpleFitXrfBounded, self).__init__("SimpleFitXrfBounded")

    def filter_frames(self, data):
        data = data[0].squeeze()[0:2048]
        in_meta_data = self.get_in_meta_data()[0]
        axis = (in_meta_data.get_meta_data("energy")[0:2048]*1e-3)/2.0
        idx = in_meta_data.get_meta_data("PeakIndex")
        positions = axis[idx]
        npts = len(idx)
        weights = data[idx]
        widths = np.ones_like(positions)*self.parameters["width_guess"]
        p = []
        p.extend(weights)
        p.extend(widths)
        widthmax=0.15
        widthmin=0.05
        weightsmax=10**5
        weightsmin=0.0
        curvetype = self.getFitFunction(str(self.parameters['peak_shape']))
        weightbounds = zip(weightsmin*np.ones(npts),weightsmax*np.ones(npts))
        widthbounds = zip(widthmin*np.ones(npts),widthmax*np.ones(npts))
        bounds = weightbounds + widthbounds
        print type(data), type(axis), type(positions), type(bounds)
        lsq1 = minimize(self._resid, p, args=(curvetype, data, axis, positions), method='L-BFGS-B',bounds=bounds)

        print "done one"
        weights, widths, areas = self.getAreas(curvetype,
                                               axis, positions, lsq1['x'])
        print lsq1['x']
        #residuals = self._resid(lsq1['x'], curvetype, data, axis, positions)
        # all fitting routines will output the same format.
        # nchannels long, with 3 elements. Each can be a subarray.
        return [weights, widths, areas, data]

    def _resid(self, p, fun, y, x, pos):
        #print fun.__name__
        r = np.linalg.norm((y-self._spectrum_sum(fun, x, pos, *p)))**2
        return r
    

        