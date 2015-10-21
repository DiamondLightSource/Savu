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
from savu.plugins.utils import register_plugin
from savu.plugins.base_fitter import BaseFitter
import numpy as np
import _xraylib as xl
from flupy.algorithms.xrf_calculations.transitions_and_shells import \
    shells, transitions
from flupy.algorithms.xrf_calculations.escape import *


@register_plugin
class BaseFluoFitter(BaseFitter):
    """
    This plugin fits peaks. Either XRD or XRF for now.
    :param in_datasets: Create a list of the dataset(s). Default: [].
    :param out_datasets: A. Default: ["FitWeights", "FitWidths", "FitAreas", "residuals"].
    :param fit_elements: List of elements of fit. Default: [].
    :param fit_range: Min max pair of fit range. Default: [].
    :param width_guess: An initial guess at the width. Default: 0.02.
    :param peak_shape: Which shape do you want. Default: "gaussian".
    """

    def __init__(self, name='BaseFluoFitter'):
        super(BaseFitter, self).__init__("BaseFitter")

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
        lsq1 = leastsq(self._resid, p, args=(curvetype, data, self.axis, positions), Dfun=dfunc, col_deriv=1)
        print "done one"
        weights, widths, areas = self.getAreas(curvetype,
                                               self.axis, positions, lsq1[0])
        residuals = self._resid(lsq1[0], curvetype, data, self.axis, positions)
        # all fitting routines will output the same format.
        # nchannels long, with 3 elements. Each can be a subarray.
        return [weights, widths, areas, residuals]

    def setPositions(self, in_meta_data):
        try:
            elements = self.parameters['fit_elements'].split(',')# a hack for now until the unicode problem is fixed
            logging.debug(elements)
            from flupy.xrf_data_handling import XRFDataset
            # assume it is like fast xrf
            paramdict = XRFDataset().paramdict
            self.axis = np.arange(0.01, 4097*0.01, 0.01)
            step = self.axis[3]-self.axis[2]
            paramdict["Experiment"]['elements'] = elements
            if self.parameters['fit_range']:
                paramdict["FitParams"]["fitted_energy_range_keV"] = \
                    self.parameters['fit_range']
#                     print paramdict["FitParams"]["fitted_energy_range_keV"]
            else:
                #  all of them
                paramdict["FitParams"]["fitted_energy_range_keV"] = \
                    [self.axis[0], self.axis[-1]]
            paramdict["Experiment"]["incident_energy_keV"] = \
                in_meta_data.get_meta_data("mono_energy")
            #print paramdict["Experiment"]["incident_energy_keV"]
#                 gives the line energy
            engy = self.findLines(paramdict)
#                 print engy
            # make it an index since this is what find peaks will also give us
            tmp = self.axis
            tmp2 = np.zeros(len(self.axis))
#                 print tmp2[self.axis < self.parameters['fit_range'][0]]
            tmp2[self.axis < self.parameters['fit_range'][0]] = 1.0
            offset = np.sum(tmp2).astype(int)
#                 print tmp2
#                 print "offset is"+str(offset)
            tmp2[self.axis > self.parameters['fit_range'][1]] = 1.0
#                 print tmp2
            tmp = self.axis[tmp2 == 0]
            self.axis = tmp # now cropped to the fitting range
#                 print tmp
            idx = (np.array(engy)/step).astype(int) - offset
            logging.debug('index '+str(sorted(idx)+offset))
            in_meta_data.set_meta_data('PeakIndex', idx)
        except Exception:
            logging.error(Exception)

    def findLines(self, paramdict):
        fitting_range = paramdict["FitParams"]["fitted_energy_range_keV"]
        energy = paramdict["Experiment"]["incident_energy_keV"]
        pileup_cut_off = 5.
        include_pileup = 1
        include_escape = 1
        detectortype = 'Vortex_SDD_Xspress'
        detector = paramdict["Detectors"][detectortype]
        detectortype = detector["detector_type"]
        no_of_transitions = 17
        fitelements = paramdict["Experiment"]['elements']
        no_of_elements = len(fitelements)
        temp_array = np.zeros((3, no_of_elements, no_of_transitions))
        peakpos = []
        for j, el in enumerate(fitelements):
            #print el
            z = xl.SymbolToAtomicNumber(str(el))
            for i, shell in enumerate(shells):
                if(xl.EdgeEnergy(z, shell) < energy-0.5):
                    linepos = 0.0
                    count = 0.0
                    for line in transitions[i]:
                        en = xl.LineEnergy(z, line)
                        if(en > 0.0):
                            linepos += en
                            count += 1.0
                            #print en
                    if(count == 0.0):
                        break
                    linepos = linepos/count

                    if(linepos > fitting_range[0]
                       and linepos < fitting_range[1]):
                        temp_array[0][j][i] = 1
                        peakpos.append(linepos)
                        if(include_pileup):
                            if(2.*linepos > fitting_range[0]
                               and 2.*linepos < fitting_range[1]
                               and 2.*linepos > pileup_cut_off):
                                temp_array[1][j][i] = 1
                                peakpos.append(2*linepos)

                        if(include_escape):
                            escape_energy = calc_escape_energy(linepos,
                                                               detectortype)
                            if(escape_energy[0] > fitting_range[0]
                               and escape_energy[0] < fitting_range[1]):
                                peakpos.append(escape_energy[0])
                                temp_array[2][j][i] = 1.
        return peakpos
