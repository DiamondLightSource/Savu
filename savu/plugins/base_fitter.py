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
   :synopsis: a base fitting plugin

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.driver.cpu_plugin import CpuPlugin

import logging
from savu.plugins.base_filter import BaseFilter
import numpy as np
import peakutils as pe
from scipy.optimize import leastsq


class BaseFitter(BaseFilter, CpuPlugin):
    """
    This plugin fits peaks. Either XRD or XRF for now.
    :param in_datasets: Create a list of the dataset(s). Default: [].
    :param out_datasets: A. Default: ["FitWeights", "FitWidths", "FitAreas", "residuals"].
    :param fit_elements: List of elements of fit. Default: [].
    :param fit_range: Min max pair of fit range. Default: [].
    :param width_guess: An initial guess at the width. Default: 0.02.
    :param peak_shape: Which shape do you want. Default: "gaussian".
    """

    def __init__(self, name='BaseFitter'):
        super(BaseFitter, self).__init__(name)

    def pre_process(self):
        logging.debug("The position index is now in the metadata")
        in_meta_data = self.get_in_meta_data()[0]
        self.setPositions(in_meta_data)
        self.positions = in_meta_data.get_meta_data('PeakIndex')
        self.fitrange = np.ones(len(self.axis))
        self.fitrange[self.axis<self.parameters['fit_range'][0]] = 0
        self.fitrange[self.axis>self.parameters['fit_range'][1]] = 0

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
        curvetype = self.lookup[str(self.parameters['peak_shape'])]
        lsq1 = leastsq(self._resid, p, args=(curvetype, data, self.axis, positions), Dfun=self.dfunc, col_deriv=1)
        print "done one"
        weights, widths, areas = self.getAreas(curvetype,
                                               self.axis, positions, lsq1[0])
        residuals = self._resid(lsq1[0], curvetype, data, self.axis, positions)
        # all fitting routines will output the same format.
        # nchannels long, with 3 elements. Each can be a subarray.
        return [weights, widths, areas, residuals]

#     def filter_frames(self, data):
#         positions = self.positions
# 
#         weights = positions
#         widths = positions
#         areas = positions
#         residuals = data
# 
#         return [weights, widths, areas, residuals]

    def setup(self):
        # set up the output datasets that are created by the plugin
        in_dataset, out_datasets = self.get_datasets()

        shape = in_dataset[0].get_shape()
        axis_labels = ['-1.peak.pixel.unit']
        pattern_list = ['SINOGRAM', 'PROJECTION']

        fitAreas = out_datasets[0]
        fitHeights = out_datasets[1]
        fitWidths = out_datasets[2]

        fitAreas.create_dataset(patterns={in_dataset[0]: pattern_list},
                                axis_labels={in_dataset[0]: axis_labels},
                                shape={'variable': shape[:-1]})

        fitHeights.create_dataset(patterns={in_dataset[0]: pattern_list},
                                  axis_labels={in_dataset[0]: axis_labels},
                                  shape={'variable': shape[:-1]})

        fitWidths.create_dataset(patterns={in_dataset[0]: pattern_list},
                                 axis_labels={in_dataset[0]: axis_labels},
                                 shape={'variable': shape[:-1]})

        channel = {'core_dir': (-1,), 'slice_dir': range(len(shape)-1)}
        
        fitAreas.add_pattern("CHANNEL", **channel)
        fitHeights.add_pattern("CHANNEL", **channel)
        fitWidths.add_pattern("CHANNEL", **channel)
        #residlabels = in_dataset[0].meta_data.get_meta_data('axis_labels')[0:3]
        #print residlabels.append(residlabels[-1])
        residuals = out_datasets[3]
        residuals.create_dataset(patterns=in_dataset[0],
                                 axis_labels=in_dataset[0],
                                 shape={'variable': shape[:-1]})


        # setup plugin datasets
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

        out_pData[0].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[1].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[2].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[3].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1

    def nOutput_datasets(self):
        return 4
    
    def setPositions(self, in_meta_data):
        try:
            positions = in_meta_data.get_meta_data('PeakIndex')
            logging.debug('Using the pre-defined PeakIndex metadata')
        except KeyError:
            logging.error('No peaks defined!')
 

    def _resid(self, p, fun, y, x, pos):
        #print fun.__name__
        r = y-self._spectrum_sum(fun, x, pos, *p)
        
        return r
    def dfunc(self, p, fun, y, x, pos):
        if fun.__name__ == 'gaussian' or fun.__name__ == 'lorentzian':
            #print fun.__name__
            rest = p
            #print "parameter shape is "+ str(p.shape)
            npts = len(p) / 2
            a = rest[:npts].astype('float64')
            sig = rest[npts:2*npts].astype('float64')
            mu = pos.astype('float64')
        #    print "len mu"+str(len(mu))
        #    print "len x"+str(len(x))
            if fun.__name__ == 'gaussian':
                print "I'm a gaussian"
                da = spectrum_sum_dfun(fun, 1./a, x, mu, *p)
                #dmu_mult = np.zeros((len(mu), len(x)))
                dsig_mult = np.zeros((len(mu), len(x)))
                for i in range(len(mu)):
                    #dmu_mult[i] = x+mu[i]
                    dsig_mult[i] = ((x-mu[i])/sig[i])-1.
                #dmu = spectrum_sum_dfun(fun, dmu_mult, x, mu, *p)
                dsig = spectrum_sum_dfun(fun, dsig_mult, x, mu, *p)
        #        print "shape of da"+str(da.shape)
                op = np.concatenate([-da, -dsig])
                #print "op.shape is "+str(op.shape)
            elif fun.__name__ == 'lorentzian':
                print "I'm a lorentzian"
                #print "hey"
                da = spectrum_sum_dfun(fun, 1./a, x, mu, *p).astype('float64')
                #dmu_mult = np.zeros((len(mu), len(x)))
                dsig_mult = np.zeros((len(mu), len(x))).astype('float64')
                for i in range(len(mu)):
                    #dmu_mult[i] = 2.0*(x-mu[i])/((x-mu[i])**2+sig[i]**2)
                    nom =  (2.0*(x-mu[i])**2)
                    denom = (sig[i]*((x-mu[i])**2+sig[i]**2))
                    dsig_mult[i] =  nom /denom # a minus here makes it work somewhat better...
                    #dsig_mult[i] = ((x-mu[i])/sig[i])-1.
                
                #print dsig_mult
                #dmu = spectrum_sum_dfun(fun, dmu_mult, x, mu, *p)
                dsig = spectrum_sum_dfun(fun, dsig_mult, x, mu, *p)
                #print sig
        #        print "shape of da"+str(da.shape)
                op = np.concatenate([-da, -dsig])
                #print "op.shape is "+str(op.shape)
        return op

    def _spectrum_sum(self, fun, x, positions, *p):
        rest = p
        npts = len(p) / 2
        weights = rest[:npts]
        #print weights
        widths = rest[npts:2*npts]
        #print widths
        spec = np.zeros((len(x),))
        for ii in range(len(weights)):
            spec += fun(weights[ii], widths[ii], x, positions[ii])
        return spec

    def getFitFunction(self,key):
        self.lookup = {
                       "lorentzian": lorentzian,
                       "gaussian": gaussian
                       }
        return self.lookup[key]

    def getAreas(self, fun, x, positions, fitmatrix):
        rest = fitmatrix
        numargsinp = 2  # 2 in
        npts = len(fitmatrix) / numargsinp
        #print npts
        weights = rest[:npts]
        print 'the weights are'+str(weights)
        widths = rest[npts:2*npts]
        print 'the widths are'+str(widths)
        #print(len(widths))
        areas = []
        for ii in range(len(weights)):
            areas.append(np.sum(fun(weights[ii],
                                    widths[ii],
                                    x,
                                    positions[ii],
                                    )))
        return weights, widths, areas

def spectrum_sum_dfun(fun, multiplier, x, pos, *p):
    rest = p
    npts = len(p) / 2
#    print npts
    weights = rest[:npts]
    print weights
    widths = rest[npts:2*npts]
    print widths
    positions = pos
#    print(len(positions))
    spec = np.zeros((npts, len(x))).astype('float64')
    #print "len x is "+str(len(spec))
#    print len(spec), type(spec)
#    print len(positions), type(positions)
#    print len(weights), type(weights)
    for ii in range(len(weights)):
        spec[ii] = multiplier[ii]*fun(weights[ii].astype('float64'),
                                      widths[ii].astype('float64'),
                                      x, positions[ii].astype('float64'))
    return spec


def lorentzian(a, w, x, c):
    w = np.abs(w)
    numerator = (w**2)
    denominator = (x - c)**2 + w**2
    y = np.abs(a)*(numerator/denominator)
    return y

    w = np.abs(w)
    numerator = (w**2)
    denominator = (x - c)**2 + w**2
    y = np.abs(a)*(numerator/denominator)
    return y


def gaussian(a, w, x, c):
    return pe.gaussian(x, a, c, w)
