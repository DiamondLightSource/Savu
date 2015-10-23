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

    def pre_process(self):
        in_dataset = self.get_in_datasets()[0]
        in_meta_data = self.get_in_meta_data()[0]
        try:
            cor = in_meta_data.get_meta_data("centre_of_rotation")
        except KeyError:
            cor = np.ones(in_dataset.get_shape()[1])
            cor *= self.parameters['center_of_rotation']
            in_meta_data.set_meta_data("centre_of_rotation", cor)
        self.exp.log(self.name + " End")
        self.cor = cor
        in_pData, out_pData = self.get_plugin_datasets()
        self.vol_shape = out_pData[0].get_shape()
        self.main_dir = in_pData[0].get_pattern()['SINOGRAM']['main_dir']
        self.angles = in_meta_data.get_meta_data('rotation_angle')

    @logmethod
    def process_frames(self, data, slice_list):
        """
        Reconstruct a single sinogram with the provided center of rotation
        """
        cor = self.cor[slice_list[0][self.main_dir]]
        return self.reconstruct(np.squeeze(data[0]), cor, self.angles,
                                self.vol_shape)

    def reconstruct(self, data, cor, angles, shape):
        """
        This is the main processing method for all plugins that inherit from
        base recon.  The plugin must implement this method.
        """
        logging.error("process needs to be implemented")
        raise NotImplementedError("process needs to be implemented")

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()
        # copy all required information from in_dataset[0]
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())

        shape = in_dataset[0].get_shape()

        dim_detX, dim_rotAngle = in_pData[0].get_core_directions()
        dim_detY = in_pData[0].get_slice_directions()[0]
        list(shape)[dim_rotAngle] = shape[dim_detX]

        dim_volX = dim_rotAngle
        dim_volY = dim_detY
        dim_volZ = dim_detX

        axis_labels = {str(dim_volX) + 'voxel_x.units',
                       str(dim_volY) + 'voxel_y.units',
                       str(dim_volZ) + 'voxel_z.units'}

        shape = (shape[2], shape[1], shape[2])

        out_dataset[0].create_dataset(axis_labels=axis_labels,
                                      shape=shape)
        out_dataset[0].add_volume_patterns(dim_volX, dim_volY, dim_volZ)

        # set pattern_name and nframes to process for all datasets
        out_pData[0].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

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
