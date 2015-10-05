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
import inspect.getargspec as howmany


@register_plugin
class SimpleFit(Filter, CpuPlugin):
    """
    This plugin fits peaks. Either XRD or XRF for now.
    :param in_datasets: Create a list of the dataset(s). Default: [].
    :param out_datasets: Create a list of the dataset(s). Default: [].
    :param fit_elements. List of elements of fit. Default: [].
    :param fit_range. Min max pair of fit range. Default: [].
    :params width_guess. An initial guess at the width. Default: 0.02.
    :params peak_shape. Which shape do you want. lorentzian|gaussian
    """

    def __init__(self):
        super(SimpleFit, self).__init__("SimpleFit")

    def pre_process(self, exp):
        """
        Let's figure out what arguments we should be passing.
        :param exp: An experiment object, holding input and output datasets
        :type exp: experiment class instance
        """
        in_meta_data, _out_meta_data = self.get_meta_data()
        if not in_meta_data.get_meta_data('PeakIndex'):
            positions = self.parameters['fit_elements']
            if isinstance(positions, str):
                from flupy.xrf_data_handling import XRFDataset
                # assume it is like fast xrf
                paramdict = {}
                axis = np.arange(0.01, 2048*0.01, 0.01)
                step = axis[3]-axis[2]
                paramdict["Experiment"]['elements'] = self.parameters['fit_elements'].split(',')
                if self.parameters['fit_range']:
                    paramdict["FitParams"]["fitted_energy_range_keV"] = self.parameters['fit_range']
                else:
                    #  all of them
                    paramdict["FitParams"]["fitted_energy_range_keV"] = [axis[0], axis[-1]]
                paramdict["Experiment"]["incident_energy_keV"] = in_meta_data.get_meta_data("mono_energy")
                idx = self.findLines(XRFDataset().paramdict)
                idx = (np.array(idx)/step).astype(int)
                #  for now
            elif isinstance(positions, list):
                axis = in_meta_data.get_meta_data('integrated_diffraction_angle')
        else:
            positions = in_meta_data.get_meta_data('PeakIndex')

        params = [positions, axis]
        return params

    def filter_frame(self, data, params):
        positions = params[0]
        axis = params[0]
        p = []
        p.extend(data[0].squeeze()[positions])
        p.extend(self.parameters['width_guess']*np.ones_like(positions))
        #  now the fit
        lsq1 = leastsq(self._resid, p, args=(data[0].squeeze(), axis, positions))

        return lsq1[0]

    def setup(self, experiment):

        self.set_experiment(experiment)
        chunk_size = self.get_max_frames()

        # get a list of input dataset names required for this plugin
        in_data_list = self.parameters["in_datasets"]
        # get all input dataset objects
        in_d1 = experiment.index["in_data"][in_data_list[0]]
        # set all input data patterns
        in_d1.set_current_pattern_name("SPECTRUM")
        # set frame chunk
        in_d1.set_nFrames(chunk_size)

        # get a list of output dataset names created by this plugin
        out_data_list = self.parameters["out_datasets"]

        # create all out_data objects and associated patterns and meta_data
        # patterns can be copied, added or both
        out_d1 = experiment.create_data_object("out_data", out_data_list[0])

        out_d1.copy_patterns(in_d1.get_patterns())
        out_d1.add_pattern("PROJECTION", core_dir=(0,), slice_dir=(0,))
        out_d1.set_current_pattern_name("1D_METADATA")
        out_d1.meta_data.set_meta_data('PeakIndex', [])
        out_d1.meta_data.copy_dictionary(in_d1.meta_data.get_dictionary(),
                                         rawFlag=True)
        # set pattern for this plugin and the shape
        out_d1.set_shape((np.prod(in_d1.data.shape[:-1]),))
        # set frame chunk
        out_d1.set_nFrames(chunk_size)

    def organise_metadata(self):
        pass

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1

    def _resid(self, p, y, x, positions):
        p = np.abs(p)
        r = y-self._spectrum_sum(self.parameters['peak_shape'], x, positions, *p)
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


    def findLines(self, paramdict):
        import _xraylib as xl
        from flupy.algorithms.xrf_calculations.transitions_and_shells import shells, transitions
        from flupy.algorithms.xrf_calculations.escape import *
        fitting_range = paramdict["FitParams"]["fitted_energy_range_keV"]
        energy = paramdict["Experiment"]["incident_energy_keV"]
        pileup_cut_off = 5.
        include_pileup = 1
        include_escape = 1
        detectortype = 'Vortex_SDD_Xspress'
        detector = paramdict["Detectors"][detectortype]
        sigma = detector["xrf_sigma"]
        tail = detector["xrf_tail_amplitude"]
        slope = detector["xrf_slope"]
        step = detector["xrf_step"]
        detectortype = detector["detector_type"]
        no_of_transitions = 17
        fitelements = 'Zn', 'Cu', 'Cr', 'Ar', 'Fe'
        no_of_elements = len(fitelements)
        DB_descript = []
        temp_array = np.zeros((3, no_of_elements, no_of_transitions))
        peakpos = []
        for j, el in enumerate(fitelements):
            #
            # loop over shells for that element
            print el
            z = xl.SymbolToAtomicNumber(str(el))
            for i, shell in enumerate(shells):
                #
                # check the edge is < energy, i.e. that it can be excited
                if(xl.EdgeEnergy(z, shell) < energy-0.5):
                    # Check the transition from that edge are
                    # within the energy range used
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
                        #
                        # is the pileup peak for this element in the
                        # fitted energy range ?
                        # Considering only double pileup..
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


def gaussian(x, weights, positions, widths):
    import peakutils as pe
    return pe.gaussian(x, weights, positions, widths)


def lorentzian(x, a, c, w):
    foo = (c-x)/(w/2.)
    curve = 1./(1.+foo**2)
    curve = a*curve
    return curve
