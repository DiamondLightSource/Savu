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
.. module:: mipmap
   :platform: Unix
   :synopsis: 'Mipmapping plugin (a pyramid-like data downampling). \
                A plugin to downsample multidimensional data

.. moduleauthor:: Mark Basham & Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

import math
import h5py
import logging
import numpy as np
import skimage.measure as skim

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class Mipmap(Plugin, CpuPlugin):
    def __init__(self):
        super(Mipmap, self).__init__("Mipmap")

    def process_frames(self, data):
        self.mode_dict = { 'mean'  : np.mean,
                           'median': np.median,
                           'min'   : np.min,
                           'max'   : np.max }
        if self.parameters['mode'] in self.mode_dict:
            sampler = self.mode_dict[self.parameters['mode']]
        else:
            logging.warning("Unknown downsample mode. Using 'mean'.")
            sampler = np.mean

        inputMap = data[0]
        res = [data[0]]
        for i in range(1,self.parameters["n_mipmaps"]):
            downsample = skim.block_reduce(inputMap, (2, 2, 2), sampler)
            res.append(downsample)
            inputMap = np.copy(downsample)

        return res

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()

        full_data_shape = list(in_dataset[0].get_shape())
        axis_labels = in_dataset[0].get_axis_labels()
        voxel_dims = \
            [i for i, e in enumerate(axis_labels) if 'voxel' in list(e.keys())[0]]

        # Sort out input data
        max_frames = self.get_max_frames()
        in_pData[0].plugin_data_setup('VOLUME_XZ', max_frames,
                slice_axis='voxel_y')

        # use this for 3D data (need to keep slice dimension)
        out_dataset = self.get_out_datasets()
        out_pData = self.get_plugin_out_datasets()

        for i in range(len(out_dataset)):
            shape = tuple([int(math.ceil(float(x)/(2**i))) if d in voxel_dims
                           else x for d, x in enumerate(full_data_shape)])
            out_dataset[i].create_dataset(axis_labels=in_dataset[0],
                                          patterns=in_dataset[0],
                                          shape=shape)
            out_pData[i].plugin_data_setup('VOLUME_XZ', max_frames // 2**i, slice_axis='voxel_y')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        n_mipmaps = self.parameters['n_mipmaps']
        name = self.parameters['out_dataset_prefix']
        self.parameters['out_datasets'] = \
            ['%s_%i' % (name, 2**i) for i in range(n_mipmaps)]
        return n_mipmaps

    def get_max_frames(self):
        return 8

    def fix_transport(self):
        return 'hdf5'
