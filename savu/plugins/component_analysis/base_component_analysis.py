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
.. module:: base_component_analysis
   :platform: Unix
   :synopsis: A base class for all component analysis methods

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
import sys
import numpy as np


class BaseComponentAnalysis(Plugin, CpuPlugin):

    def __init__(self, name):
        super(BaseComponentAnalysis, self).__init__(name)

    def get_max_frames(self):
        return self.spectra_length[0]

    def get_plugin_pattern(self):
        return self.parameters['chunk']

    def setup(self):
        self.exp.log(self.name + " Setting up the component analysis")
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        self.spectra_length = (in_dataset[0].get_shape()[-1],)
        other_dims = in_dataset[0].get_shape()[:-1]
        num_comps = self.parameters['number_of_components']
        self.images_shape = other_dims + (num_comps,)
        components_shape = (num_comps,) + self.spectra_length
        # copy all required information from in_dataset[0]

        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=self.images_shape)

        axis_labels = ['idx.unit', 'spectra.unit']
        out_dataset[1].create_dataset(shape=components_shape,
                                      axis_labels=axis_labels)
        spectrum = {'core_dims': (1,), 'slice_dims': (0,)}

        out_dataset[1].add_pattern("SPECTRUM", **spectrum)

        in_pData, out_pData = self.get_plugin_datasets()
        plugin_pattern = self.get_plugin_pattern()
#         dirs = range(len(out_dataset[0].get_shape()))
#         vxz = {'core_dims': (0,1), 'slice_dims': (2,)}
#         in_dataset[0].add_pattern("VOLUME_XZ", **vxz)
        in_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())
        out_pData[0].plugin_data_setup(plugin_pattern, num_comps)
        out_pData[1].plugin_data_setup("SPECTRUM", num_comps)

        self.exp.log(self.name + " End")

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 2

    def remove_nan_inf(self, data):
        '''
        converts the nans to nums and sets the infs to the max float size
        not strictly true, but does allow fitting to take place
        '''
        data = np.clip(data,-sys.float_info.max,sys.float_info.max)
        data[np.isnan(data)]=0
        data = np.nan_to_num(data)
        return data
