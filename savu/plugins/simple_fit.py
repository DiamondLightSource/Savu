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
from savu.plugins.driver.cpu_plugin import CpuPlugin


from savu.plugins.utils import register_plugin
from savu.plugins.base_filter import BaseFilter
import numpy as np
from scipy.optimize import leastsq
from inspect import getargspec as howmany
import peakutils as pe
#import _xraylib as xl
#from flupy.algorithms.xrf_calculations.transitions_and_shells import \
#    shells, transitions
#from flupy.algorithms.xrf_calculations.escape import *


@register_plugin
class SimpleFit(BaseFilter, CpuPlugin):
    """
    This plugin fits peaks. Either XRD or XRF for now.
    :param in_datasets: Create a list of the dataset(s). Default: [].
    :param out_datasets: A. Default: ["FitWeights", "FitWidths", "FitAreas", "residuals"].
    :param fit_elements: List of elements of fit. Default: [].
    :param fit_range: Min max pair of fit range. Default: [].
    :param width_guess: An initial guess at the width. Default: 0.02.
    :param peak_shape: Which shape do you want. Default: "gaussian".
    """

    def __init__(self):
        super(SimpleFit, self).__init__("SimpleFit")

    def pre_process(self):
        self.setPositions(self.get_in_meta_data()[0])

#    def filter_frames(self, data):
#        positions = self.positions
#        axis = self.axis
#        p = []
#        p.extend(data[0].squeeze()[positions])
#        p.extend(self.parameters['width_guess']*np.ones_like(positions))
#        #  now the fit
#        lsq1 = leastsq(self._resid, p,
#                       args=(data[0].squeeze(), axis, positions))
#        weights, widths, areas = self.getAreas(self.parameters['peak_shape'],
#                                               axis, positions, lsq1[0])
#        residuals = self._resid(lsq1[0], data[0].squeeze(), axis, positions)
#        # all fitting routines will output the same format.
#        # nchannels long, with 3 elements. Each can be a subarray.
#        return [weights, widths, areas, residuals]

    def filter_frames(self, data):
        positions = self.positions

        weights = positions
        widths = positions
        areas = positions
        residuals = data

        return [weights, widths, areas, residuals]

    def setup(self):
        # set up the output datasets that are created by the plugin
        in_dataset, out_datasets = self.get_datasets()

        shape = in_dataset[0].get_shape()
        axis_labels = {in_dataset[0]: '-1.peak.pixel'}
        pattern_list = ['SINOGRAM', 'PROJECTION']

        fitAreas = out_datasets[0]
        fitHeights = out_datasets[1]
        fitWidths = out_datasets[2]

        fitAreas.create_dataset(patterns={in_dataset[0]: pattern_list},
                                axis_labels=axis_labels,
                                shape={'variable': shape[:-1]})

        fitHeights.create_dataset(patterns={in_dataset[0]: pattern_list},
                                  axis_labels=axis_labels,
                                  shape={'variable': shape[:-1]})

        fitWidths.create_dataset(patterns={in_dataset[0]: pattern_list},
                                 axis_labels=axis_labels,
                                 shape={'variable': shape[:-1]})

        channel = {'core_dir': (-1,), 'slice_dir': range(len(shape)-1)}
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

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1

    def nOutput_datasets(self):
        return 4

    def _resid(self, p, y, x, positions):
        p = np.abs(p)
        r = y-self._spectrum_sum(self.parameters['peak_shape'],
                                 x, positions, *p)
        return r

    def _spectrum_sum(self, fun, x, positions, *p):
        rest = p
        numargsinp = len(howmany(fun)[0])-2  # 2 in
        npts = len(p) / numargsinp
        print npts
        weights = rest[:npts]
        print(len(weights))
        widths = rest[npts:2*npts]
        print widths
        print(len(widths))
        spec = np.zeros(x.shape)
        for ii in range(len(weights)):
            spec += fun(x, weights[ii], positions[ii], widths[ii])
        return spec

    def setPositions(self, in_meta_data):
        try:
            positions = in_meta_data.get_meta_data('PeakIndex')
        except KeyError:
            positions = self.parameters['fit_elements']

            if isinstance(positions, str):
                from flupy.xrf_data_handling import XRFDataset
                # assume it is like fast xrf
                paramdict = {}
                axis = np.arange(0.01, 2048*0.01, 0.01)
                step = axis[3]-axis[2]
                paramdict["Experiment"]['elements'] = \
                    self.parameters['fit_elements'].split(',')
                if self.parameters['fit_range']:
                    paramdict["FitParams"]["fitted_energy_range_keV"] = \
                        self.parameters['fit_range']
                else:
                    #  all of them
                    paramdict["FitParams"]["fitted_energy_range_keV"] = \
                        [axis[0], axis[-1]]
                paramdict["Experiment"]["incident_energy_keV"] = \
                    in_meta_data.get_meta_data("mono_energy")
                idx = self.findLines(XRFDataset().paramdict)
                idx = (np.array(idx)/step).astype(int)
                #  for now
            elif isinstance(positions, list):
                axis = \
                    in_meta_data.get_meta_data('integrated_diffraction_angle')

        self.positions = positions

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
            print el
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
                            print en
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

    def getAreas(self, fun, x, positions, fitmatrix):
        rest = fitmatrix
        numargsinp = len(howmany(fun)[0])-2  # 2 in
        npts = len(fitmatrix) / numargsinp
        print npts
        weights = rest[:npts]
        print(len(weights))
        widths = rest[npts:2*npts]
        print widths
        print(len(widths))
        areas = []
        for ii in range(len(weights)):
            areas.append(np.sum(fun(x,
                                    weights[ii],
                                    positions[ii],
                                    widths[ii])))
        return weights, widths, areas

    def gaussian(self, x, weights, positions, widths):
        return pe.gaussian(x, weights, positions, widths)

    def lorentzian(self, x, a, c, w):
        foo = (c-x)/(w/2.)
        curve = 1./(1.+foo**2)
        curve = a*curve
        return curve
