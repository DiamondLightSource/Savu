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
.. module:: reproduce_fit
   :platform: Unix
   :synopsis: A plugin to regenerate the fitted curves

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
from savu.plugins.utils import register_plugin
from savu.plugins.fitters.base_fitter import BaseFitter
import numpy as np
from copy import deepcopy

#@register_plugin
class ReproduceFit(BaseFitter):

    def __init__(self):
        super(ReproduceFit, self).__init__("ReproduceFit")

    def pre_process(self):
        self.function = self.getFitFunction(self.parameters['peak_shape'])

    def process_frames(self, data):
        FitWeights,FitWidths, _FitAreas,Backgrounds = data
        npts = len(FitWeights)
        params = []
        params.extend(FitWeights)
        params.extend(FitWidths) 
        Sum = self._spectrum_sum(self.function, self.energy, self.PeakEnergy, *params) + Backgrounds
        Individual_curves = np.zeros((len(self.PeakEnergy), len(self.energy)))
        for i in range(npts):
            Individual_curves[i,:] = self.function(FitWeights[i], FitWidths[i], self.energy, self.PeakEnergy[i]) + Backgrounds
        return [Sum, Individual_curves]

    def setup(self):
        # set up the output datasets that are created by the plugin
        in_dataset, out_datasets = self.get_datasets()

        shape = in_dataset[-1].get_shape()

        summed = out_datasets[0]
        individual_curves = out_datasets[1]

        self.PeakEnergy = in_dataset[0].meta_data.get('PeakEnergy')
        self.energy = in_dataset[-1].meta_data.get('energy')

        new_shape = shape[:-1] + (len(self.PeakEnergy),) + (shape[-1],)
#         print "the new shape is"+str(new_shape)

        summed.create_dataset(in_dataset[-1])
        individual_curves.create_dataset(patterns=in_dataset[-1],
                                  axis_labels={in_dataset[-1]: ['~-2.idx.unit']},
                                  shape=new_shape)

        ss_slice = list(range(len(new_shape) - 2))
#         print "spectrum stack slice dims are" + str(ss_slice)
        spectrum_stack = {'core_dims': (-2, -1), 'slice_dims': tuple(ss_slice)}

        individual_curves.add_pattern("SPECTRUM_STACK", **spectrum_stack)

        # setup plugin datasets
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('CHANNEL', self.get_max_frames())
        in_pData[1].plugin_data_setup('CHANNEL', self.get_max_frames())
        in_pData[2].plugin_data_setup('CHANNEL', self.get_max_frames())
        in_pData[3].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[1].plugin_data_setup("SPECTRUM_STACK", self.get_max_frames())


    def nInput_datasets(self):
        return 4
    
    def nOutput_datasets(self):
        return 2
