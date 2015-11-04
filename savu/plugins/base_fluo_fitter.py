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

import logging
from savu.plugins.base_fitter import BaseFitter
import numpy as np
import _xraylib as xl
from flupy.algorithms.xrf_calculations.transitions_and_shells import \
    shells, transitions
from flupy.algorithms.xrf_calculations.escape import *
from flupy.xrf_data_handling import XRFDataset


class BaseFluoFitter(BaseFitter):
    """
    This plugin fits peaks. Either XRD or XRF for now.
    :param in_datasets: Create a list of the dataset(s). Default: [].
    :param out_datasets: A. Default: ["FitWeights", "FitWidths", "FitAreas", "residuals"].
    :param width_guess: An initial guess at the width. Default: 0.02.
    :param peak_shape: Which shape do you want. Default: "gaussian".
    :param pileup_cutoff_keV: The cut off. Default: 5.5.
    :param include_pileup: Include pileup. Default: 1.
    :param include_escape: Include escape. Default: 1.
    :param fitted_energy_range_keV: The fitted energy range. Default: [2.,18.].
    :param elements: The fitted elements. Default: ['Zn','Cu', 'Ar'].
    """

    def __init__(self, name="BaseFluoFitter"):
        super(BaseFluoFitter, self).__init__(name)

    def pre_process(self):
        in_meta_data = self.get_in_meta_data()[0]
        try:
            _foo = in_meta_data.get_meta_data("PeakIndex")[0]
            logging.debug('Using the positions in the peak index')
        except KeyError:
            logging.debug("No Peak Index in the metadata")
            logging.debug("Calculating the positions from energy")
            idx = self.setPositions(in_meta_data)
            #print "The index is"+str(idx)
            in_meta_data.set_meta_data('PeakIndex', idx)

    def setup(self):
        # set up the output datasets that are created by the plugin
        in_dataset, out_datasets = self.get_datasets()

        shape = in_dataset[0].get_shape()
        axis_labels = ['-1.PeakIndex.pixel.unit']
        pattern_list = ['SINOGRAM', 'PROJECTION']

        fitAreas = out_datasets[0]
        fitHeights = out_datasets[1]
        fitWidths = out_datasets[2]
        numpeaks = 10 
        new_shape = shape[:-1] + (numpeaks,)
        print new_shape
        fitAreas.create_dataset(patterns={in_dataset[0]: pattern_list},
                                axis_labels={in_dataset[0]: axis_labels},
                                shape=new_shape)

        fitHeights.create_dataset(patterns={in_dataset[0]: pattern_list},
                                  axis_labels={in_dataset[0]: axis_labels},
                                  shape=new_shape)

        fitWidths.create_dataset(patterns={in_dataset[0]: pattern_list},
                                 axis_labels={in_dataset[0]: axis_labels},
                                 shape=new_shape)

        channel = {'core_dir': (-1,), 'slice_dir': range(len(shape)-1)}
        
        fitAreas.add_pattern("CHANNEL", **channel)
        fitHeights.add_pattern("CHANNEL", **channel)
        fitWidths.add_pattern("CHANNEL", **channel)
        #residlabels = in_dataset[0].meta_data.get_meta_data('axis_labels')[0:3]
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
        paramdict["Experiment"]["incident_energy_keV"] = \
            in_meta_data.get_meta_data("mono_energy")
        paramdict["Experiment"]["elements"] = \
            self.parameters["elements"]
        engy = self.findLines(paramdict)
#                 print engy
        # make it an index since this is what find peaks will also give us
        axis = in_meta_data.get_meta_data("energy")
        print engy
        print "the axis is"+str(axis)
        dq = axis[1]-axis[0]
        print 'dq is '+str(dq)
        idx = np.round(engy/dq).astype(int)
        print "The index is"
        print len(idx)
        return idx

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
                    linepos = linepos/count
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
        print peakpos
        return peakpos
