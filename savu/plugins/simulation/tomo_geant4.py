# Copyright 2019 Diamond Light Source Ltd.
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
.. module:: A wrapper for Geant4TomoSim software (Oliver Wenmann)
   :platform: Unix
   :synopsis: Geant4TomoSim uses Geant4 to realistically simulate tomographic data

.. moduleauthor:: Daniil Kazantsev & Oliver Wenmann <scientificsoftware@diamond.ac.uk>
"""

import savu.plugins.utils as pu
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

# import *

import os
#from savu.data.plugin_list import CitationInformation
import numpy as np

@register_plugin
class TomoGeant4(Plugin, CpuPlugin):
    """
    Description of __Geant4TomoSim__

    :param proj_num: The number of projections. Default: 360.
    :param detectors_X The number of (horizontal) detectors. Default:256.
    :param detectors_X The number of (vertical) detectors. Default:200.
    :param out_datasets: Default out dataset names. Default: ['projection']
    """

    def __init__(self):
        super(TomoGeant4, self).__init__('TomoGeant4')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def setup(self):
        in_dataset, self.out_dataset = self.get_datasets()
        #out_dataset[0].create_dataset(in_dataset[0])
        in_pData, self.out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        self.out_shape = self.new_shape(in_dataset[0].get_shape(), in_dataset[0])

        self.out_dataset[0].create_dataset(patterns=in_dataset[0],
                                           axis_labels=in_dataset[0],
                                           shape=self.out_shape)
        self.out_pData[0].plugin_data_setup('SINOGRAM', 'single')

        # generate angles
        self.angles = np.linspace(0.0,179.9,self.parameters['proj_num'],dtype='float32')
        self.out_dataset[0].meta_data.set('rotation_angle', self.angles)

    def new_shape(self, full_shape, data):
        # example of a function to calculate a new output data shape based on
        # the input data shape
        core_dirs = data.get_core_dimensions()
        new_shape = list(full_shape)
        print "New shape is", new_shape.shape
        new_shape= (self.parameters['proj_num'], new_shape[1], self.parameters['detectors_X'])
        return tuple(new_shape)
    def pre_process(self):
        # set parameters for __Geant4TomoSim__:
        self.proj_num = self.parameters['proj_num']
        self.detectors_X = self.parameters['detectors_X']
        self.detectors_Y = self.parameters['detectors_Y']
        #print "The full data shape is", self.get_in_datasets()[0].get_shape()
        #print "Example is", self.parameters['example']
    def process_frames(self, data):
        print "The input data shape is", data[0].shape
        # TODO:  GENERATE projection data
        #projdata = np.zeros()
        return projdata
    def post_process(self):
        pass
