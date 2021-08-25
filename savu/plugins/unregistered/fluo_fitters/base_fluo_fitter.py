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
.. module:: base_fluo_fitter
   :platform: Unix
   :synopsis: a base fitting plugin

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

import logging
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
import peakutils as pe
import numpy as np
import xraylib as xl
from flupy.algorithms.xrf_calculations.transitions_and_shells import \
    shells, transitions
from flupy.algorithms.xrf_calculations.escape import *
from flupy.xrf_data_handling import XRFDataset
from copy import deepcopy


class BaseFluoFitter(Plugin, CpuPlugin):
    def __init__(self, name="BaseFluoFitter"):
        super(BaseFluoFitter, self).__init__(name)

    def base_pre_process(self):
        in_meta_data = self.get_in_meta_data()[0]
        try:
            _foo = in_meta_data.get("PeakIndex")[0]
            logging.debug('Using the positions in the peak index')
        except KeyError:
            logging.debug("No Peak Index in the metadata")
            logging.debug("Calculating the positions from energy")
#             idx = self.setPositions(in_meta_data)
            logging.debug("The index is"+str(self.idx))
            in_meta_data.set('PeakIndex', self.idx)
            in_meta_data.set('PeakEnergy', self.axis[self.idx])

    def setup(self):
        # set up the output datasets that are created by the plugin
        logging.debug('setting up the fluorescence fitting')
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_meta_data = in_dataset[0].meta_data

        shape = in_dataset[0].get_shape()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

        axis_labels = ['-1.PeakIndex.pixel.unit']
        pattern_list = ['SINOGRAM', 'PROJECTION']

        fitAreas = out_datasets[0]
        fitWidths = out_datasets[1]
        fitHeights = out_datasets[2]
        self.length = shape[-1]
        idx = self.setPositions(in_meta_data)
        logging.debug("in the setup the index is"+str(idx))
        numpeaks = len(idx)
        new_shape = shape[:-1] + (numpeaks,)

        channel = {'core_dims': (-1,), 'slice_dims': list(range(len(shape)-1))}
        fitAreas.create_dataset(patterns={in_dataset[0]: pattern_list},
                                axis_labels={in_dataset[0]: axis_labels},
                                shape=new_shape)
        fitAreas.add_pattern("CHANNEL", **channel)
        out_pData[0].plugin_data_setup('CHANNEL', self.get_max_frames())

        fitWidths.create_dataset(patterns={in_dataset[0]: pattern_list},
                                 axis_labels={in_dataset[0]: axis_labels},
                                 shape=new_shape)
        fitWidths.add_pattern("CHANNEL", **channel)
        out_pData[1].plugin_data_setup('CHANNEL', self.get_max_frames())

        fitHeights.create_dataset(patterns={in_dataset[0]: pattern_list},
                                  axis_labels={in_dataset[0]: axis_labels},
                                  shape=new_shape)
        fitHeights.add_pattern("CHANNEL", **channel)
        out_pData[2].plugin_data_setup('CHANNEL', self.get_max_frames())

        residuals = out_datasets[3]
        residuals.create_dataset(in_dataset[0])
        residuals.set_shape(shape[:-1]+(len(self.axis),))
        out_pData[3].plugin_data_setup('SPECTRUM', self.get_max_frames())

        for i in range(len(out_datasets)):
            out_datasets[i].meta_data = deepcopy(in_meta_data)
            mData = out_datasets[i].meta_data
            mData.set("PeakEnergy", self.axis[self.idx])
            mData.set('PeakIndex', self.idx)

    def setPositions(self, in_meta_data):
        paramdict = XRFDataset().paramdict
        paramdict["FitParams"]["pileup_cutoff_keV"] = \
            self.parameters["pileup_cutoff_keV"]
        paramdict["FitParams"]["include_pileup"] = \
            self.parameters["include_pileup"]
        paramdict["FitParams"]["include_escape"] = \
            self.parameters["include_escape"]
        paramdict["FitParams"]["fitted_energy_range_keV"] = \
            self.parameters["fitted_energy_range_keV"]
        if self.parameters['mono_energy'] is None:
            paramdict["Experiment"]["incident_energy_keV"] = \
                in_meta_data.get("mono_energy")
        else:
            paramdict["Experiment"]["incident_energy_keV"] = \
                self.parameters['mono_energy']
        paramdict["Experiment"]["elements"] = \
            self.parameters["elements"]
        engy = self.findLines(paramdict)
        # make it an index since this is what find peak will also give us
#         print 'basefluo meta is:'+str(in_meta_data.get_dictionary().keys())
        axis = self.axis = in_meta_data.get("energy")
        dq = axis[1]-axis[0]
        logging.debug("the peak energies are:"+str(engy))
        logging.debug("the offset is"+str(axis[0]))
        self.idx = np.round((engy-axis[0])/dq).astype(int)

        return self.idx

    def findLines(self, paramdict=XRFDataset().paramdict):
        """
        Calculates the line energies to fit
        """
        # Incident Energy  used in the experiment
        # Energy range to use for fitting
        pileup_cut_off = paramdict["FitParams"]["pileup_cutoff_keV"]
        include_pileup = paramdict["FitParams"]["include_pileup"]
        include_escape = paramdict["FitParams"]["include_escape"]
        fitting_range = paramdict["FitParams"]["fitted_energy_range_keV"]
#         x = paramdict["FitParams"]["mca_energies_used"]
        energy = paramdict["Experiment"]["incident_energy_keV"]
        detectortype = 'Vortex_SDD_Xspress'
        fitelements = paramdict["Experiment"]["elements"]
        peakpos = []
        escape_peaks = []
        for _j, el in enumerate(fitelements):
            z = xl.SymbolToAtomicNumber(str(el))
            for i, shell in enumerate(shells):
                if(xl.EdgeEnergy(z, shell) < energy - 0.5):
                    linepos = 0.0
                    count = 0.0
                    for line in transitions[i]:
                        en = xl.LineEnergy(z, line)
                        if(en > 0.0):
                            linepos += en
                            count += 1.0
                    if(count == 0.0):
                        break
                    linepos = linepos // count
                    if(linepos > fitting_range[0] and
                            linepos < fitting_range[1]):
                        peakpos.append(linepos)
        peakpos = np.array(peakpos)
        too_low = set(list(peakpos[peakpos > fitting_range[0]]))
        too_high = set(list(peakpos[peakpos < fitting_range[1]]))
        bar = list(too_low and too_high)
        bar = np.unique(bar)
        peakpos = list(bar)
        peaks = []
        peaks.extend(peakpos)
        if(include_escape):
            for i in range(len(peakpos)):
                escape_energy = calc_escape_energy(peakpos[i], detectortype)[0]
                if (escape_energy > fitting_range[0]):
                    if (escape_energy < fitting_range[1]):
                        escape_peaks.extend([escape_energy])
    #         print escape_peaks
            peaks.extend(escape_peaks)

        if(include_pileup):  # applies just to the fluorescence lines
            pileup_peaks = []
            peakpos1 = np.array(peakpos)
            peakpos_high = peakpos1[peakpos1 > pileup_cut_off]
            peakpos_high = list(peakpos_high)
            for i in range(len(peakpos_high)):
                foo = [peakpos_high[i] + x for x in peakpos_high[i:]]
                foo = np.array(foo)
                pileup_peaks.extend(foo)
            pileup_peaks = np.unique(sorted(pileup_peaks))
            peaks.extend(pileup_peaks)
        peakpos = peaks
        peakpos = np.array(peakpos)
        too_low = set(list(peakpos[peakpos > fitting_range[0]]))
        too_high = set(list(peakpos[peakpos < fitting_range[1] - 0.5]))
        bar = list(too_low and too_high)
        bar = np.unique(bar)
        peakpos = list(bar)
        peakpos = np.unique(peakpos)
#         print peakpos
        return peakpos

    def getAreas(self, fun, x, positions, fitmatrix):
        rest = fitmatrix
        numargsinp = self.getFitFunctionNumArgs(str(fun.__name__))  # 2 in
        npts = len(fitmatrix) // numargsinp
        weights = rest[:npts]
        widths = rest[npts:2*npts]
        areas = []
        for ii in range(len(weights)):
            areas.append(np.sum(fun(weights[ii],
                                    widths[ii],
                                    x,
                                    positions[ii],
                                    )))
        return weights, widths, np.array(areas)

    def getFitFunctionNumArgs(self,key):
        self.lookup = {
                       "lorentzian": 2,
                       "gaussian": 2
                       }
        return self.lookup[key]

    def get_max_frames(self):
        return 'single'

    def nOutput_datasets(self):
        return 4

    def getFitFunction(self,key):
        self.lookup = {
                       "lorentzian": lorentzian,
                       "gaussian": gaussian
                       }
        return self.lookup[key]

    def _resid(self, p, fun, y, x, pos):
        r = y-self._spectrum_sum(fun, x, pos, *p)

        return r

    def dfunc(self, p, fun, y, x, pos):
        if fun.__name__ == 'gaussian' or fun.__name__ == 'lorentzian': # took the lorentzian out. Weird
            rest = p
            npts = len(p) // 2
            a = rest[:npts]
            sig = rest[npts:2*npts]
            mu = pos
            if fun.__name__ == 'gaussian':
                da = self.spectrum_sum_dfun(fun, 1./a, x, mu, *p)
                dsig_mult = np.zeros((npts, len(x)))
                for i in range(npts):
                    dsig_mult[i] = ((x-mu[i])**2) / sig[i]**3
                dsig = self.spectrum_sum_dfun(fun, dsig_mult, x, mu, *p)
                op = np.concatenate([-da, -dsig])
            elif fun.__name__ == 'lorentzian':
                da = self.spectrum_sum_dfun(fun, 1./a, x, mu, *p)
                dsig = np.zeros((npts, len(x)))
                for i in range(npts):
                    nom = 8 * a[i] * sig[i] * (x - mu[i]) ** 2
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

    def spectrum_sum_dfun(self, fun, multiplier, x, pos, *p):
        rest = p
        npts = len(p) // 2
        weights = rest[:npts]
        widths = rest[npts:2*npts]
        positions = pos
    #    print(len(positions))
        spec = np.zeros((npts, len(x)))
        #print "len x is "+str(len(spec))
    #    print len(spec), type(spec)
    #    print len(positions), type(positions)
    #    print len(weights), type(weights)
        for ii in range(len(weights)):
            spec[ii] = multiplier[ii]*fun(weights[ii],
                                          widths[ii],
                                          x, positions[ii])
        return spec

def lorentzian(a, w, x, c):
    y = a / (1.0 + (2.0 * (c - x) / w) ** 2)
    return y


def gaussian(a, w, x, c):
    return pe.gaussian(x, a, c, w)


