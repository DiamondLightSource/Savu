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
.. module:: base_fitter
   :platform: Unix
   :synopsis: a base class for all fitting methods

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
from savu.plugins.plugin import Plugin
import numpy as np
import peakutils as pe
from savu.plugins.driver.cpu_plugin import CpuPlugin


class BaseFitter(Plugin, CpuPlugin):

    def __init__(self, name='BaseFitter'):
        super(BaseFitter, self).__init__(name)

    def setup(self):
        # set up the output datasets that are created by the plugin
        in_dataset, out_datasets = self.get_datasets()

        shape = in_dataset[0].get_shape()
        outshape = tuple(shape[:-1])+(self.parameters('PeakIndex'),)
        axis_labels = ['-1.PeakIndex.pixel.unit']
        pattern_list = ['SINOGRAM', 'PROJECTION']

        fitAreas = out_datasets[0]
        fitHeights = out_datasets[1]
        fitWidths = out_datasets[2]

        fitAreas.create_dataset(patterns={in_dataset[0]: pattern_list},
                                axis_labels={in_dataset[0]: axis_labels},
                                shape=outshape)

        fitHeights.create_dataset(patterns={in_dataset[0]: pattern_list},
                                  axis_labels={in_dataset[0]: axis_labels},
                                  shape=outshape)

        fitWidths.create_dataset(patterns={in_dataset[0]: pattern_list},
                                 axis_labels={in_dataset[0]: axis_labels},
                                 shape=outshape)

        channel = {'core_dims': (-1,), 'slice_dims': list(range(len(shape)-1))}

        fitAreas.add_pattern("CHANNEL", **channel)
        fitHeights.add_pattern("CHANNEL", **channel)
        fitWidths.add_pattern("CHANNEL", **channel)
        #residlabels = in_dataset[0].meta_data.get('axis_labels')[0:3]
        #print residlabels.append(residlabels[-1])
        residuals = out_datasets[3]
        residuals.create_dataset(in_dataset[0])


        # setup plugin datasets
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

        out_pData[0].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[1].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[2].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[3].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        return 'single'

    def nOutput_datasets(self):
        return 4

    def setPositions(self, in_meta_data):
        try:
            positions = in_meta_data.get('PeakIndex')
            logging.debug('Using the pre-defined PeakIndex metadata')
        except KeyError:
            logging.error('No peaks defined!')

    def _resid(self, p, fun, y, x, pos):
        #print fun.__name__
        r = y-self._spectrum_sum(fun, x, pos, *p)

        return r

    def dfunc(self, p, fun, y, x, pos):
        if fun.__name__ == 'gaussian' or fun.__name__ == 'lorentzian':  # took the lorentzian out. Weird
            rest = p
            npts = len(p) // 2
            a = rest[:npts]
            sig = rest[npts:2*npts]
            mu = pos
            if fun.__name__ == 'gaussian':
                da = self.spectrum_sum_dfun(fun, 1. / a, x, mu, *p)
                dsig_mult = np.zeros((npts, len(x)))
                for i in range(npts):
                    dsig_mult[i] = ((x-mu[i])**2) / sig[i]**3
                dsig = self.spectrum_sum_dfun(fun, dsig_mult, x, mu, *p)
                op = np.concatenate([-da, -dsig])
            elif fun.__name__ == 'lorentzian':
                da = self.spectrum_sum_dfun(fun, 1. / a, x, mu, *p)
                dsig = np.zeros((npts, len(x)))
                for i in range(npts):
                    nom = 8 * a[i]* sig[i] * (x - mu[i]) ** 2
                    denom = (sig[i]**2 + 4.0 * (x - mu[i])**2)**2
                    dsig[i] = nom / denom
                op = np.concatenate([-da, -dsig])
        else:
            op = None
        return op

    def _spectrum_sum(self, fun, x, positions, *p):
        rest = np.abs(p)
        npts = len(p) // 2
        weights = rest[:npts]
        widths = rest[npts:2*npts]
        spec = np.zeros((len(x),))
        for ii in range(len(weights)):
            spec += fun(weights[ii], widths[ii], x, positions[ii])
        return spec

    def getFitFunction(self, key):
        self.lookup = {"lorentzian": lorentzian, "gaussian": gaussian}
        return self.lookup[key]

    def getFitFunctionNumArgs(self, key):
        self.lookup = {"lorentzian": 2, "gaussian": 2}
        return self.lookup[key]

    def getAreas(self, fun, x, positions, fitmatrix):
        rest = fitmatrix
        numargsinp = self.getFitFunctionNumArgs(str(fun.__name__))  # 2 in
        npts = len(fitmatrix) // numargsinp
        weights = rest[:npts]
        #print 'the weights are'+str(weights)
        widths = rest[npts:2*npts]
        #print 'the widths are'+str(widths)
        #print(len(widths))
        areas = []
        for ii in range(len(weights)):
            areas.append(np.sum(fun(weights[ii],
                                    widths[ii],
                                    x,
                                    positions[ii],
                                    )))
        return weights, widths, np.array(areas)

    def spectrum_sum_dfun(self, fun, multiplier, x, pos, *p):
        rest = p
        npts = len(p) // 2
        weights = rest[:npts]
        widths = rest[npts:2*npts]
        positions = pos
        spec = np.zeros((npts, len(x)))
        for ii in range(len(weights)):
            spec[ii] = multiplier[ii]*fun(weights[ii], widths[ii], x, positions[ii])
        return spec


def lorentzian(a, w, x, c):
    y = a / (1.0 + (2.0 * (c - x) / w) ** 2)
    return y


def gaussian(a, w, x, c):
    return pe.gaussian(x, a, c, w)
