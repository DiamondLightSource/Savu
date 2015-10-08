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

    def process_frames(self, sinogram, frame_list):
        """
        Reconstruct a single sinogram with the provided center of rotation
        """
        logging.error("reconstruct needs to be implemented")
        raise NotImplementedError("reconstruct " +
                                  "needs to be implemented")

#    @logmethod
#    def process(self, transport):
#        """
#        Perform the main processing step for the plugin
#        """
#        in_data, out_data = self.get_plugin_datasets()
#        in_meta_data, out_meta_data = self.get_meta_data()
#
#        try:
#            centre_of_rotation = \
#                in_meta_data[0].get_meta_data("centre_of_rotation")
#        except KeyError:
#            centre_of_rotation = np.ones(in_data[0].data_obj.get_shape()[1])
#            centre_of_rotation *= self.parameters['center_of_rotation']
#            in_meta_data[0].set_meta_data("centre_of_rotation",
#                                          centre_of_rotation)
#
#        transport.reconstruction_setup(self, in_data[0], out_data[0],
#                                       self.exp)

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # copy all required information from in_dataset[0]

        out_dataset[0].add_volume_patterns()
        axis_labels = ['voxel_x.units', 'voxel_y.units', 'voxel_z.units']
        shape = in_dataset[0].get_shape()

        out_dataset[0].create_dataset(axis_labels=axis_labels,
                                      shape=(shape[2], shape[1], shape[2]))

        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()
        # set pattern_name and nframes to process for all datasets
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())
        out_pData[0].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

        self.exp.log(self.name + " End")

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
