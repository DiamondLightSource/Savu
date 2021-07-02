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
import logging
from savu.plugins.utils import register_plugin
from savu.plugins.fitters.base_fitter import BaseFitter
import numpy as np
from scipy.optimize import leastsq
import time
import math

@register_plugin
class SimpleFit(BaseFitter):

    def __init__(self):
        super(SimpleFit, self).__init__("SimpleFit")

    def pre_process(self):
        in_meta_data = self.get_in_meta_data()[0]
        out_meta_data = self.get_out_meta_data()[0]
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
        [x2, cov_x2, infodict2, msg2, ier2] = leastsq(self._resid, p,
                       args=(curvetype, data, axis, positions),
                       Dfun=self.dfunc, col_deriv=1, full_output=1)
        logging.debug("done one")
        params = x2
        if np.isnan(params).any():
            logging.debug('Nans were detected here')
            params = np.zeros(len(params))
        #print msg2
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

        if len(peakindex) == 0:
            raise Exception("Please specify the PeakIndex")
        
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
