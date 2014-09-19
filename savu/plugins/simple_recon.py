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
.. module:: simple_recon
   :platform: Unix
   :synopsis: A simple implementation a reconstruction routine for testing
       purposes

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.data.structures import ProjectionData, VolumeData
from savu.plugins.plugin import Plugin

import numpy as np


class SimpleRecon(Plugin):
    """
    A Plugin to apply a simple reconstruction with no dependancies
    """

    def __init__(self):
        super(SimpleRecon, self).__init__("SimpleRecon")

    def populate_default_parameters(self):
        self.parameters['center_of_rotation'] = 86

    def _filter(self, sinogram):
        ff = np.arange(sinogram.shape[0])
        ff -= sinogram.shape[0]/2
        ff = np.abs(ff)
        fs = np.fft.fft(sinogram)
        ffs = fs*ff
        return np.fft.ifft(ffs).real

    def _back_project(self, mapping, sino_element, center):
        mapping_array = mapping+center
        return sino_element[mapping_array.astype('int')]

    def _mapping_array(self, shape, center, theta):
        x, y = np.meshgrid(np.arange(-center[0], shape[0] - center[0]),
                           np.arange(-center[1], shape[1]-center[1]))
        return x*np.cos(theta) - y*np.sin(theta)

    def _reconstruct(self, sinogram, centre_of_rotation, shape, center):
        result = np.zeros(shape)
        for i in range(sinogram.shape[0]):
            theta = i * (np.pi/sinogram.shape[0])
            mapping_array = self._mapping_array(shape, center, theta)
            filt = np.zeros(sinogram.shape[1]*3)
            filt[sinogram.shape[1]:sinogram.shape[1]*2] = \
                self._filter(sinogram[i, :])
            result += \
                self._back_project(mapping_array, filt,
                                   (centre_of_rotation + sinogram.shape[1]))
        return result

    def process(self, data, output, processes, process):
        """
        """
        centre_of_rotation = self.parameters['center_of_rotation']

        sinogram_frames = np.arange(data.get_number_of_sinograms())

        frames = np.array_split(sinogram_frames, processes)[process]

        for frame in frames:
            sinogram = data.data[:, frame, :]
            sinogram = np.log(sinogram)
            reconstruction = \
                self._reconstruct(sinogram, centre_of_rotation,
                                  (output.data.shape[0], output.data.shape[2]),
                                  (output.data.shape[0]/2,
                                   output.data.shape[2]/2))
            output.data[:, frame, :] = reconstruction

    def required_resource(self):
        """
        This plugin needs to use the CPU to work

        :returns:  CPU
        """
        return "CPU"

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
