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
.. module:: fastxrf_fitting
   :platform: Unix
   :synopsis: A plugin to fit XRF spectra quickly

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging
from savu.plugins.unregistered.fluo_fitters.base_fluo_fitter \
    import BaseFluoFitter
from flupy.xrf_data_handling import XRFDataset
import numpy as np
from savu.plugins.utils import register_plugin


#@register_plugin
class FastxrfFitting(BaseFluoFitter):
    def __init__(self):
        logging.debug("Starting fast fitter")
        super(FastxrfFitting, self).__init__("FastxrfFitting")

    def base_pre_process(self):
        pass

    def pre_process(self):
        """
        This method is called after the plugin has been created by the
        pipeline framework as a pre-processing step.
        """
        in_meta_data = self.get_in_meta_data()[0]
        self.xrfd = self.prep_xrfd(in_meta_data)

    def process_frames(self, data):
        logging.debug("Running azimuthal integration")
        xrfd = self.xrfd
#         print np.squeeze(data).shape
        xrfd.datadict['data'] = np.squeeze(data)
#         print "I'm here"
        xrfd.fitbatch()
        characteristic_curves = xrfd.matrixdict["Total_Matrix"]
        weights = xrfd.fitdict['parameters']
        full_curves = characteristic_curves*weights
        areas = full_curves.sum(axis=0)
#         print "the shape is :" + str(characteristic_curves.shape)
        return [weights, areas, xrfd.fitdict['resid']]

    def setPositions(self, in_meta_data):
        '''
        overload this to get the right setup method
        '''
        xrfd = self.prep_xrfd(in_meta_data)
        numcurves = xrfd.matrixdict['Total_Matrix'].shape[1]
        idx = np.ones((numcurves,))
        return idx
    
    
    def prep_xrfd(self, in_meta_data):
        self.axis = in_meta_data.get("energy")
        xrfd = XRFDataset()
        # now to overide the experiment
        xrfd.paramdict["Experiment"] = {}
        xrfd.paramdict["Experiment"]["incident_energy_keV"] = \
            self.parameters["mono_energy"]
#         print xrfd.paramdict["Experiment"]["incident_energy_keV"]
        xrfd.paramdict["Experiment"]["collection_time"] = 1
        xrfd.paramdict["Experiment"]['Attenuators'] = \
            self.parameters['sample_attenuators']
        xrfd.paramdict["Experiment"]['detector_distance'] = \
            self.parameters['detector_distance']
        xrfd.paramdict["Experiment"]['elements'] = \
            self.parameters['elements']
        xrfd.paramdict["Experiment"]['incident_angle'] = \
            self.parameters['incident_angle']
        xrfd.paramdict["Experiment"]['exit_angle'] = \
            self.parameters['exit_angle']
        xrfd.paramdict["Experiment"]['photon_flux'] = self.parameters['flux']

        # overide the fitting parameters
        xrfd.paramdict["FitParams"]["background"] = 'strip'
        xrfd.paramdict["FitParams"]["fitted_energy_range_keV"] = self.parameters["fitted_energy_range_keV"]
        xrfd.paramdict["FitParams"]["include_pileup"] = self.parameters["include_pileup"]
        xrfd.paramdict["FitParams"]["include_escape"] = self.parameters["include_escape"]
        datadict = {}
        datadict["rows"] = self.get_max_frames()
        datadict["cols"] = 1 # we will just treat it as one long row
        datadict["average_spectrum"] = np.zeros_like(self.axis)
        datadict["Detectors"] = {}
        datadict["Detectors"]["type"] = 'Vortex_SDD_Xspress'
        xrfd.xrfdata(datadict)
        xrfd._createSpectraMatrix()
        if xrfd.paramdict['FitParams']['mca_energies_used']==self.axis:
            pass
        else:
            self.axis = xrfd.paramdict['FitParams']['mca_energies_used']
        return xrfd