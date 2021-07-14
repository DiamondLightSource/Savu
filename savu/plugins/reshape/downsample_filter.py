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
.. module:: downsample_filter
   :platform: Unix
   :synopsis: A plugin to downsample and rescale data volume.

.. moduleauthor:: Mark Basham, Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy as np
import skimage.measure as skim
from scipy.ndimage import rotate

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
import savu.core.utils as cu


@register_plugin
class DownsampleFilter(Plugin, CpuPlugin):
    def __init__(self):
        super(DownsampleFilter, self).__init__("DownsampleFilter")
        self.out_shape = None
        self.mode_dict = { 'mean'  : np.mean,
                           'median': np.median,
                           'min'   : np.min,
                           'max'   : np.max }

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        self.pattern = self.parameters['pattern']
        self.num_bit = self.parameters['num_bit']
        self.bin_size = int(self.parameters["bin_size"])
        if self.pattern == "SINOGRAM" or self.pattern == "PROJECTION":
            in_pData[0].plugin_data_setup(self.pattern, 'single')
            self.out_shape = \
                self.get_new_shape(in_dataset[0].get_shape(), in_dataset[0])

            out_dataset[0].create_dataset(patterns=in_dataset[0],
                                          axis_labels=in_dataset[0],
                                          shape=self.out_shape)
            out_pData[0].plugin_data_setup(self.pattern, 'single')
        elif self.pattern == "VOLUME_XZ":
            full_data_shape = list(in_dataset[0].get_shape())
            axis_labels = in_dataset[0].get_axis_labels()
            voxel_dims = [i for i, e in enumerate(axis_labels)
                          if 'voxel' in list(e.keys())[0]]
            in_pData[0].plugin_data_setup('VOLUME_XZ', self.bin_size,
                                          slice_axis='voxel_y')
            shape = tuple([int(np.ceil(float(x) / self.bin_size))
                           if d in voxel_dims
                           else x for d, x in enumerate(full_data_shape)])
            if self.num_bit == 8:
                dtype = "uint8"
            elif self.num_bit == 16:
                dtype = "uint16"
            else:
                dtype = "float32"
            out_dataset[0].create_dataset(axis_labels=in_dataset[0],
                                          patterns=in_dataset[0],
                                          shape=shape, dtype = dtype)
            out_pData[0].plugin_data_setup('VOLUME_XZ', 1,
                                           slice_axis='voxel_y')
        else:
            raise ValueError("\nPlease select one of three options:"
                             " 'SINOGRAM', 'PROJECTION', 'VOLUME_XZ'\n")

    def pre_process(self):
        if self.pattern == "VOLUME_XZ":
            if not (self.num_bit == 8 or self.num_bit == 16
                     or self.num_bit == 32):
                self.num_bit = 32
            if self.num_bit == 8 or self.num_bit == 16:
                self.global_min = self.parameters['min']
                self.global_max = self.parameters['max']
                if self.global_min is None or self.global_max is None:
                    self.data_range = self.get_min_and_max()
                    if self.global_min is None:
                        self.global_min = self.data_range[0]
                    if self.global_max is None:
                        self.global_max = self.data_range[1]

    def process_frames(self, data):
        if self.parameters['mode'] in self.mode_dict:
            sampler = self.mode_dict[self.parameters['mode']]
        else:
            logging.warning("Unknown downsample mode. Using 'mean'.")
            sampler = np.mean
        flip_ud = self.parameters['flip_updown']
        flip_lr = self.parameters['flip_leftright']
        rotate_angle = self.parameters['rotate_angle']
        data_used = data[0]
        if self.pattern == 'SINOGRAM' or self.pattern == 'PROJECTION':
            if (rotate_angle != 0.0) and self.pattern == 'PROJECTION':
                data_used = rotate(data_used, rotate_angle, reshape=False,
                                   mode='nearest')
            if flip_ud is True:
                data_used = np.flipud(data_used)
            if flip_lr is True:
                data_used = np.fliplr(data_used)
            block_size = (self.bin_size, self.bin_size)
            downsample = skim.block_reduce(data_used, block_size, sampler)
        else:
            num_slice = data_used.shape[1]
            block_size = (self.bin_size, self.bin_size, self.bin_size)
            if flip_ud is True:
                data_used = np.moveaxis(np.asarray([np.flipud(data_used[:, i, :])
                                        for i in range(num_slice)]), 0 , 1)
            if flip_lr is True:
                data_used = np.moveaxis(np.asarray([np.fliplr(data_used[:, i, :])
                                        for i in range(num_slice)]), 0, 1)
            if rotate_angle != 0.0:
                data_used = np.moveaxis(np.asarray([rotate(data_used[:, i, :],
                                        rotate_angle, reshape=False,
                                        mode='nearest')
                                        for i in range(num_slice)]), 0, 1)
            if self.num_bit == 8 or self.num_bit == 16:
                data_used = np.clip(data_used, self.global_min, self.global_max)
                data_used = (data_used - self.global_min) \
                            / (self.global_max - self.global_min)
                downsample = skim.block_reduce(data_used, block_size, sampler)
                if self.num_bit == 8:
                    downsample = np.uint8(downsample * 255)
                else:
                    downsample = np.uint16(downsample * 65535)
            else:
                downsample = skim.block_reduce(data_used, block_size, sampler)
        return downsample

    def get_new_shape(self, full_shape, data):
        core_dirs = data.get_core_dimensions()
        new_shape = list(full_shape)
        for dim in core_dirs:
            new_shape[dim] = full_shape[dim] // self.bin_size
            if (full_shape[dim] % self.bin_size) > 0:
                new_shape[dim] += 1
        return tuple(new_shape)

    def get_min_and_max(self):
        data = self.get_in_datasets()[0]
        pattern = 'VOLUME_XZ'
        try:
            self.the_min = np.min(
                data.meta_data.get(['stats', 'min', pattern]))
            self.the_max = np.max(
                data.meta_data.get(['stats', 'max', pattern]))
            self.data_range = (self.the_min, self.the_max)
        except KeyError:
            msg = str("\n***********************************************\n" 
                "!!!Error!!!-> No global maximum and global minimum found\n"
                "in the metadata. Please run the MaxAndMin plugin before\n"  
                "this plugin or input manually. \n" 
                "***********************************************\n")
            cu.user_message(msg)
            raise ValueError(msg)
        return self.data_range

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def fix_transport(self):
        return 'hdf5'
