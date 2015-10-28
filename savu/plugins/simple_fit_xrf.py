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
from savu.plugins.utils import register_plugin
from savu.plugins.base_fluo_fitter import BaseFluoFitter
import numpy as np
from scipy.optimize import leastsq
import time


@register_plugin
class SimpleFitXrf(BaseFluoFitter):
    """
    This plugin fits XRF peaks.
    :param width_guess: An initial guess at the width. Default: 0.02.

    """
    def __init__(self):
        super(SimpleFitXrf, self).__init__("SimpleFitXrf")

    def filter_frames(self, data):
        t1 = time.time()
        data = data[0].squeeze()
        print "the shape is: "+str(data.shape)
        in_meta_data = self.get_in_meta_data()[0]
        axis = (in_meta_data.get_meta_data("energy")*1e-3)/2.0
        idx = in_meta_data.get_meta_data("PeakIndex")
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

        print "done one"
        weights, widths, areas = self.getAreas(curvetype,
                                               axis, positions, lsq1[0])
        print lsq1[0]
        residuals = self._resid(lsq1[0], curvetype, data, axis, positions)
        t2 = time.time()
        print "Simple fit iteration took:"+str((t2-t1)*1e3)+"ms"
        # all fitting routines will output the same format.
        # nchannels long, with 3 elements. Each can be a subarray.
        return [weights, widths, areas, residuals]

