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
from savu.plugins.filter import Filter
import numpy as np
from scipy.optimize import leastsq
from inspect import getargspec as howmany
import peakutils as pe
import _xraylib as xl
from flupy.algorithms.xrf_calculations.transitions_and_shells import \
    shells, transitions
from flupy.algorithms.xrf_calculations.escape import *


@register_plugin
class SimpleFit(Filter, CpuPlugin):
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
        in_meta_data, _out_meta_data = self.get_meta_data()
        if not in_meta_data.get_meta_data('PeakIndex'):
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
                self.axis = \
                    in_meta_data.get_meta_data('integrated_diffraction_angle')
        else:
            self.positions = in_meta_data.get_meta_data('PeakIndex')

    def filter_frame(self, data):
        positions = self.positions
        axis = self.axis
        p = []
        p.extend(data[0].squeeze()[positions])
        p.extend(self.parameters['width_guess']*np.ones_like(positions))
        #  now the fit
        lsq1 = leastsq(self._resid, p,
                       args=(data[0].squeeze(), axis, positions))
        weights, widths, areas = self.getAreas(self.parameters['peak_shape'],
                                               axis, positions, lsq1[0])
        residuals = self._resid(lsq1[0], data[0].squeeze(), axis, positions)
        # all fitting routines will output the same format.
        # nchannels long, with 3 elements. Each can be a subarray.
        return [weights, widths, areas, residuals]

    def setup(self, experiment):

        # set up the output datasets that are created by the plugin
        in_datasets, out_datasets = self.get_datasets()
        mData = in_datasets[0].meta_data.get_dictionary()
        
        axis_labels = [in_datasets[0], '-1.name.unit']
        positions = self.get_positions(mData)
        shape = in_dataset[0].get_shape() + (len(positions),)
        channel = {'core_dir': (-1,), 'slice_dir': range(len(outshape)-1)}
        acq_patterns = in_dataset[0].get_patterns_based_on_acquisition()
        print "acquisition based patterns", acq_patterns

        for out_data in out_datasets[:-1]:
            out_data.create_dataset(patterns=in_dataset[0],
                                    axis_labels=axis_labels, shape=shape)
            out_data.add_pattern("CHANNEL", **channel)
            for acq in acq_patterns:
                out_data.add_pattern(acq.keys()[0], acq[acq.keys()[0]]
        
        residuals = out_datasets[-1]
        residuals.set_shape(outshape+(len(positions),))
        residuals.add_pattern("SPECTRUM",core_dir=(-1,),slice_dir=) # copy all patterns from in_data
        # add spectrum and set current pattern name to be spectrum, axis labels?
        # add acq_patterns

        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()

        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

        for out_data in out_datasets[:-1]
            out_pData[0].plugin_data_setup('CHANNEL', self.get_max_frames())

        out_pData[-1].plugin_data_setup('SPECTRUM', self.get_max_frames())

#    def setup(self, experiment):
#
#        # set up the output dataset that is created by the plugin
#        in_dataset, out_dataset = self.get_datasets()
#        in_meta_data, out_meta_data = self.get_meta_data()
#
#        out_dataset[0].create_dataset(in_dataset[0])
#        outshape = in_dataset[0].get_shape()
#        positions = self.getPositions(in_meta_data[0])
#        out_dataset[0].set_shape(outshape+(len(positions),))
#        out_meta_data[0][]
#
#
#        chunk_size = self.get_max_frames()
#        # get a list of input dataset names required for this plugin
#        in_data_list = self.parameters["in_datasets"]
#        # get all input dataset objects
#        in_d1 = experiment.index["in_data"][in_data_list[0]]
#        # set all input data patterns
#        in_d1.set_current_pattern_name("SPECTRUM")
#        # set frame chunk
#        outshape = in_d1.get_shape()
#        in_d1.set_nFrames(chunk_size)
#        # Ok.So how many peaks will we fit?
#
#        positions = self.getPositions(in_meta_data)
#
#        FitAreas = experiment.create_data_object("out_data", "FitAreas")
#        FitAreas.set_shape(outshape+(len(positions),))
#        FitAreas.add_pattern("CHANNEL", core_dir=(-1,),
#                             slice_dir=range(len(outshape)-1))
#        FitAreas.set_current_pattern_name("CHANNEL")
#        FitHeights = experiment.create_data_object("out_data", "FitHeights")
#        FitHeights.set_shape(outshape+(len(positions),))
#        FitHeights.add_pattern("CHANNEL", core_dir=(-1,),
#                               slice_dir=range(len(outshape)-1))
#        FitHeights.set_current_pattern_name("CHANNEL")
#        FitWidths = experiment.create_data_object("out_data", "FitWidths")
#        FitWidths.set_shape(outshape+(len(positions),))
#        FitWidths.add_pattern("CHANNEL", core_dir=(-1,),
#                              slice_dir=range(len(outshape)-1))
#        FitWidths.set_current_pattern_name("CHANNEL")
#
#        residuals = experiment.create_data_object("out_data", "residuals")
#        residuals.set_shape(outshape+(len(positions),))
#        # now the tomo/map stuff
#        for out_d1 in self.parameters["out_datasets"]:
#            motor_type = in_meta_data.get_meta_data("motor_type")
#            projection = []
#            projection_slice = []
#            for item, key in enumerate(motor_type):
#                if key == 'translation':
#                    projection.append(item)
#                elif key != 'translation':
#                    projection_slice.append(item)
#                if key == 'rotation':
#                    rotation = item  # we will assume one rotation for now
#            projdir = tuple(projection)
#            if in_meta_data.get_meta_data("is_map"):
#                ndims = range(len(outshape))
#                ovs = []
#                for i in ndims:
#                    if i != projdir[0]:
#                        if i != projdir[1]:
#                            ovs.append(i)
#                out_d1.add_pattern("PROJECTION", core_dir=projdir,
#                                   slice_dir=ovs)
#            if in_meta_data.get_meta_data("is_tomo"):
#                ndims = range(len(outshape))
#                ovs = []
#                for i in ndims:
#                    if i != rotation:
#                        if i != projdir[1]:
#                            ovs.append(i)
#                out_d1.add_pattern("SINOGRAM",
#                                   core_dir=(rotation, projdir[-1]),
#                                   slice_dir=ovs)

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1

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

    def getPositions(self, in_meta_data):
        if not in_meta_data.get_meta_data('PeakIndex'):
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
        else:
            positions = in_meta_data.get_meta_data('PeakIndex')
        return positions

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
