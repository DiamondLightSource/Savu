# -*- coding: utf-8 -*-
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

logging.debug("Importing packages in base_recon")

from savu.plugins.plugin import Plugin
from savu.core.utils import logmethod

import numpy as np


class BaseRecon(Plugin):
    """
    A Plugin to apply a simple reconstruction with no dependancies

    :param center_of_rotation: Centre of rotation to use for the reconstruction). Default: 86.
    :param in_datasets: Create a list of the dataset(s) to process. Default: [].
    :param out_datasets: Create a list of the dataset(s) to process. Default: [].

    """
    count = 0

    def __init__(self, name='BaseRecon'):
        super(BaseRecon, self).__init__(name)

    def reconstruct(self, sinogram, centre_of_rotations, vol_shape):
        """
        Reconstruct a single sinogram with the provided center of rotation
        """
        logging.error("reconstruct needs to be implemented")
        raise NotImplementedError("reconstruct " +
                                  "needs to be implemented")

    @logmethod
    def process(self, transport):
        """
        Perform the main processing step for the plugin
        """
        in_data, out_data = self.get_plugin_datasets()
        in_meta_data, out_meta_data = self.get_meta_data()

        try:
            centre_of_rotation = \
                in_meta_data[0].get_meta_data("centre_of_rotation")
        except KeyError:
            centre_of_rotation = np.ones(in_data[0].data_obj.get_shape()[1])
            centre_of_rotation *= self.parameters['center_of_rotation']
            in_meta_data[0].set_meta_data("centre_of_rotation",
                                          centre_of_rotation)

        transport.reconstruction_setup(self, in_data[0], out_data[0],
                                       self.exp)

    def setup(self):
        self.exp.log(self.name + " Start")

        # Input datasets setup
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(pattern_name='SINOGRAM',
                                      chunk=self.get_max_frames())

        # set details for all output data sets
        shape = in_pData[0].data_obj.get_shape()
        out_pData[0].plugin_data_setup(pattern_name='VOLUME_XZ',
                                       chunk=self.get_max_frames(),
                                       shape=(shape[2], shape[1], shape[2]))

        # copy or add patterns related to this dataset
        out_pData[0].data_obj.add_volume_patterns()

        self.exp.log(self.name + " End")

    def organise_metadata(self):
        pass

    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at
        a time

        :returns:  an integer of the number of frames
        """
        return 8

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

logging.debug("Completed base_recon import")
