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
from savu.plugins.base_fitter import BaseFitter
import numpy as np
from scipy.optimize import leastsq


@register_plugin
class SimpleFit(BaseFitter):
    """
    This plugin fits peaks. Either XRD or XRF for now.
    :param in_datasets: Create a list of the dataset(s). Default: [].
    :param out_datasets: A. Default: ["FitWeights", "FitWidths", "FitAreas", "residuals"].
    :param fit_range: Min max pair of fit range. Default: [].
    :param width_guess: An initial guess at the width. Default: 0.02.
    :param peak_shape: Which shape do you want. Default: "lorentzian".
    """

    def __init__(self):
        super(SimpleFit, self).__init__("SimpleFit")

    def filter_frames(self, data):
        databig = data[0].squeeze()
        data = databig[self.fitrange == 1]
        weights = data[self.positions]
        #print weights
        positions = self.axis[self.positions]
        widths = np.ones_like(positions)*0.02
        #print widths
        p = []
        p.extend(weights)
        p.extend(widths)
        curvetype = self.getFitFunction(str(self.parameters['peak_shape']))
        lsq1 = leastsq(self._resid, p,
                       args=(curvetype, data, self.axis, positions),
                       Dfun=self.dfunc, col_deriv=1)
        print "done one"
        weights, widths, areas = self.getAreas(curvetype,
                                               self.axis, positions, lsq1[0])
        residuals = self._resid(lsq1[0], curvetype, data, self.axis, positions)
        # all fitting routines will output the same format.
        # nchannels long, with 3 elements. Each can be a subarray.
        return [weights, widths, areas, residuals]

