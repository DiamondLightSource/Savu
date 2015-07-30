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
.. module:: base_recon
   :platform: Unix
   :synopsis: A simple implementation a reconstruction routine for testing
       purposes

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.data.structures import ProjectionData, VolumeData
from savu.plugins.plugin import Plugin
from savu.core.utils import logmethod

import numpy as np


class BaseRecon(Plugin):
    """
    A Plugin to apply a simple reconstruction with no dependancies
    
    :param center_of_rotation: Center of rotation to use for the reconstruction). Default: 86.
    """
    count = 0

    def __init__(self, name='BaseRecon'):
        super(BaseRecon, self).__init__(name)

    def reconstruct(self, sinogram, centre_of_rotation, angles, shape, center):
        """
        Reconstruct a single sinogram with the provided center of rotation
        """
        logging.error("reconstruct needs to be implemented")
        raise NotImplementedError("reconstruct " +
                                  "needs to be implemented")

    
    @logmethod
    def process(self, data, output, processes, process, transport):
        """
        """
        if data.center_of_rotation is None:
            centre_of_rotation = np.ones(data.get_number_of_sinograms())
            centre_of_rotation = centre_of_rotation * self.parameters['center_of_rotation']
        else :
            centre_of_rotation = data.center_of_rotation[:]
        
        if centre_of_rotation is None:
            centre_of_rotation = np.ones(data.get_number_of_sinograms())
            centre_of_rotation = centre_of_rotation * self.parameters['center_of_rotation']

        angles = data.rotation_angle.data[:]
        centre_of_rotations = np.array_split(centre_of_rotation, len(processes))[process]
                
        params = [centre_of_rotations, angles] 
        
        transport.process(self, data, output, processes, process, 
                          params, "reconstruction_set_up")                
                          
            
    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at a time

        :returns:  an integer of the number of frames
        """
        return 8

    def required_data_type(self):
        """
        The input for this plugin is ProjectionData

        :returns:  ProjectionData
        """
        return ProjectionData

    def output_data_type(self):
        """
        The output of this plugin is VolumeData

        :returns:  VolumeData
        """
        return VolumeData

    def input_dist(self):
        """
        The input DistArray distribution for this plugin is "nbn"
        (i.e. block in the second dimension)

        :returns:  DistArray distribution
        """
        return "nbn"

    def output_dist(self):
        """
        The output DistArray distribution for this plugin is "nbn"
        (i.e. block in the second dimension)

        :returns:  DistArray distribution
        """
        return "nbn"