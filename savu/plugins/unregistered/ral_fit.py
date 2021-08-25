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
.. module:: ral_fit
   :platform: Unix
   :synopsis: A plugin to fit peaks

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
from savu.plugins.utils import register_plugin
from savu.plugins.fitters.base_fitter import BaseFitter
import numpy as np
from scipy.optimize import leastsq
import time
import math
import ral_nlls

#@register_plugin
class RalFit(BaseFitter):
    """
    This plugin fits peaks.
    :param width_guess: An initial guess at the width. Default: 0.02.
    """

    def __init__(self):
        super(RalFit, self).__init__("RalFit")

    def pre_process(self):
        in_meta_data = self.get_in_meta_data()[0]
        in_meta_data.set("PeakIndex", self.parameters["PeakIndex"])
        self.axis = in_meta_data.get("Q")
        self.peakindex = in_meta_data.get("PeakIndex")
        self.positions = self.axis[self.peakindex]
        in_meta_data.set('PeakQ', self.positions)

    def process_frames(self, data):
        t1 = time.time()
        data = data[0]
        axis = self.axis
        positions = self.positions
        #print positions
        weights = data[self.peakindex]
        widths = np.ones_like(positions)*self.parameters["width_guess"]
        p = []
        p.extend(weights)
        p.extend(widths)
        curvetype = self.getFitFunction(str(self.parameters['peak_shape']))
        #print "HI"
        [x1, infodict1] = ral_nlls.solve(
                    p, self._resid, self.dfunc,
                    params=(curvetype, data, axis, positions),
                                      options = {
                                          'print_level': 3,
                                          'maxit': 100,
                                          'model': 1,
                                          'nlls_method': 4,
                                          'stop_g_absolute': 1e-7,
                                          'stop_g_relative': 1e-7,
                                          'relative_tr_radius': 0,
                                          'initial_radius_scale': 1.0,
                                          'maximum_radius': 1e8,
                                          'eta_successful':1e-8,
                                          'eta_success_but_reduce': 1e-8,
                                          'eta_very_successful':0.9,
                                          'eta_too_successful': 2.0,
                                          'radius_increase': 2.0,
                                          'radius_reduce': 0.5,
                                          'radius_reduce_max': 1/16,
                                          'tr_update_strategy': 2,
                                          'hybrid_switch': 1e-0,
                                          'scale': 0,
                                          'scale_max':1e11,
                                          'scale_min':1e-11,
                                          'more_sorensen_maxits': 500,
                                          'more_sorensen_shift': 1e-13,
                                          'more_sorensen_tol': 1e-3,
                                          'hybrid_tol': 2.0,
                                          'hybrid_switch_its': 1
                                      })

        logging.debug("done one")
        params = x1[0]
        if np.isnan(params).any():
            logging.debug('Nans were detected here')
            params = np.zeros(len(params))

        weights, widths, areas = self.getAreas(curvetype,
                                               axis, positions, params)
        residuals = self._resid(params, curvetype, data, axis, positions)
        # all fitting routines will output the same format.
        # nchannels long, with 3 elements. Each can be a subarray.
        t2 = time.time()
        logging.debug("Simple fit iteration took: %s ms", str((t2-t1)*1e3))
        return [weights, widths, areas, residuals]

    def setup(self):
        # set up the output datasets that are created by the plugin
        in_dataset, out_datasets = self.get_datasets()

        shape = in_dataset[0].get_shape()
        axis_labels = ['-1.PeakIndex.pixel.unit']
        pattern_list = ['SINOGRAM', 'PROJECTION']

        fitAreas = out_datasets[0]
        fitHeights = out_datasets[1]
        fitWidths = out_datasets[2]
        peakindex = self.parameters['PeakIndex']
        new_shape = shape[:-1] + (len(peakindex),)

        fitAreas.create_dataset(patterns={in_dataset[0]: pattern_list},
                                axis_labels={in_dataset[0]: axis_labels},
                                shape=new_shape)

        fitHeights.create_dataset(patterns={in_dataset[0]: pattern_list},
                                  axis_labels={in_dataset[0]: axis_labels},
                                  shape=new_shape)

        fitWidths.create_dataset(patterns={in_dataset[0]: pattern_list},
                                 axis_labels={in_dataset[0]: axis_labels},
                                 shape=new_shape)

        channel = {'core_dims': (-1,), 'slice_dims': list(range(len(shape)-1))}

        fitAreas.add_pattern("CHANNEL", **channel)
        fitHeights.add_pattern("CHANNEL", **channel)
        fitWidths.add_pattern("CHANNEL", **channel)

        residuals = out_datasets[3]
        residuals.create_dataset(in_dataset[0])

        # setup plugin datasets
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

        out_pData[0].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[1].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[2].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[3].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def dfunc(self, p, fun, y, x, pos):
    #     print fun.__name__
        print("Here")
        rest = p
        npts = len(p) // 2
        order = 1
        if (order == 1):
            a = rest[:npts].astype('float64')
            sig = rest[npts:2*npts].astype('float64')
        elif (order == 2):
            a = rest[0::2].astype('float64')
            sig = rest[1::2].astype('float64')
        else:
            raise NameError('Bad value of order')
        mu = pos.astype('float64')
        da = self.spectrum_sum_dfun(fun, 1. / a, x, mu, order, *p).astype('float64')

        dsig = np.zeros((npts, len(x)))
        for i in range(npts):
            nom = 8 * a[i] * sig[i] * (x - mu[i]) ** 2
            denom = (sig[i]**2 + 4.0 * (x - mu[i])**2)**2
            dsig[i] = nom / denom
    #     op = np.concatenate([-da, -dsig])
        if (order == 1):
            op = np.concatenate([-da, -dsig])
        elif (order == 2):
            op = np.empty((2 * npts, len(y)))
            op[::2,:] = -da
            op[1::2,:] = -dsig

#         if (transpose == 1):
        op = np.transpose(op)

        return op
