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

import numpy as np


class BaseRecon(Plugin):
    """
    A Plugin to apply a simple reconstruction with no dependancies
    """

    def __init__(self, name='BaseRecon'):
        super(BaseRecon, self).__init__(name)

    def populate_default_parameters(self):
        self.parameters['center_of_rotation'] = 86

    def reconstruct(self, sinogram, centre_of_rotation, angles, shape, center):
        """
        Reconstruct a single sinogram with the provided center of rotation
        """
        logging.error("reconstruct needs to be implemented")
        raise NotImplementedError("reconstruct " +
                                  "needs to be implemented")

    def process(self, data, output, processes, process):
        """
        """
        centre_of_rotation = data.center_of_rotation[:]
        if centre_of_rotation is None:
            centre_of_rotation = np.ones(data.get_number_of_sinograms())
            centre_of_rotation = centre_of_rotation * self.parameters['center_of_rotation']

        sinogram_frames = np.arange(data.get_number_of_sinograms())

        frames = np.array_split(sinogram_frames, len(processes))[process]
        centre_of_rotations =\
            np.array_split(centre_of_rotation, len(processes))[process]

        angles = data.rotation_angle.data[:]

        for i in range(len(frames)):
            frame_centre_of_rotation = centre_of_rotations[i]
            sinogram = data.data[:, frames[i], :]
            reconstruction = \
                self.reconstruct(sinogram, frame_centre_of_rotation, angles,
                                 (output.data.shape[0], output.data.shape[2]),
                                 (output.data.shape[0]/2,
                                  output.data.shape[2]/2))
            output.data[:, frames[i], :] = reconstruction

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
