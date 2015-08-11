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

from savu.plugins.plugin import Plugin
from savu.core.utils import logmethod
import savu.data.data_structures as ds

import numpy as np


class BaseRecon(Plugin):
    """
    A Plugin to apply a simple reconstruction with no dependancies
    
    :param center_of_rotation: Centre of rotation to use for the reconstruction). Default: 86.
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
    def process(self, exp, transport):
        """
        """
        in_data = exp.index["in_data"]["tomo"]
        out_data = exp.index["out_data"]["tomo"]

        if "centre_of_rotation" not in exp.info:
            centre_of_rotation = np.ones(in_data.get_nPattern())
            centre_of_rotation = centre_of_rotation * self.parameters['center_of_rotation']
            exp.meta_data.set_meta_data("centre_of_rotation", centre_of_rotation)
                        
        transport.reconstruction_setup(self, in_data, out_data, exp.info)                        


    def setup(self, experiment):
        
        in_data = experiment.index["in_data"]["tomo"]
        in_data.set_pattern_name("SINOGRAM")
        in_data.check_data_type_exists()

        base_classes = [ds.Pattern]
        experiment.info["base_classes"] = base_classes
        out_data = experiment.create_data_object("out_data", "tomo", base_classes)            
        out_data.copy_patterns(in_data.info["data_patterns"])

        out_data = experiment.index["out_data"]["tomo"]
        out_data.set_pattern_name("VOLUME_XZ")
        out_data.check_data_type_exists()
        shape = in_data.get_shape()
        out_data.set_shape((shape[2], shape[1], shape[2]))
     
            
    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at a time

        :returns:  an integer of the number of frames
        """
        return 8
