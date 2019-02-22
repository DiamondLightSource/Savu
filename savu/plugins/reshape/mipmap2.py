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
.. module:: mipmap2
   :platform: Unix
   :synopsis: A plugin render some slices from a volume and save them as images
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.driver.cpu_plugin import CpuPlugin

import os
import copy
import logging

import skimage.measure as skim

import matplotlib.pyplot as plt

import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)


@register_plugin
class Mipmap2(Plugin, CpuPlugin):
    """
    A plugin to calculate the centre of rotation using the Vo Method

    :u*param xy_slices: which XY slices to render. Default: 100.
    :u*param yz_slices: which YZ slices to render. Default: 100.
    :u*param xz_slices: which XZ slices to render. Default: 100.
    :u*param file_type: File type to save as. Default: 'png'.
    :u*param colourmap: Colour scheme to apply to the image. Default: 'magma'.
    :param out_datasets: Default out dataset names. Default: ['XY', 'YZ', 'XZ']
    """

    def __init__(self):
        super(Mipmap2, self).__init__("Mipmap2")

    def pre_process(self):
        pass

    def process_frames(self, data):
        self.exp.log("XXXX Starting to run process_frames in Orthoslice")
        print("XXXX Starting to run process_frames in Orthoslice")

        in_dataset = self.get_in_datasets()
        out_datasets = self.get_out_datasets()

        fullData = in_dataset[0]

        out0 = out_datasets[0]
        out1 = out_datasets[1]
        out2 = out_datasets[2]

        ext = self.parameters['file_type']
        in_plugin_data = self.get_plugin_in_datasets()[0]
        pos = in_plugin_data.get_current_frame_idx()

        self.exp.log("frame position is %s" % (str(pos)))

        mipmap_info = [(out0, data[0], 1),
                       (out1, skim.block_reduce(data[0], (2, 2, 2), np.mean), 2),
                       (out2, skim.block_reduce(data[0], (4, 4, 4), np.mean), 4)]

        # Set up the output list
        output_slices = []

        # mipmap levels
        for output_dataset, data, size in mipmap_info:
            # build the slice list
            slice_to_take = [slice(None)]*len(fullData.data.shape)

            slice_to_take[in_plugin_data.get_slice_dimension()] = pos[0,len(pos)/size]

            out0[slice_to_take] = output_dataset[...]

        return None

    def populate_meta_data(self, key, value):
        datasets = self.parameters['datasets_to_populate']
        in_meta_data = self.get_in_meta_data()[0]
        in_meta_data.set(key, value)
        for name in datasets:
            self.exp.index['in_data'][name].meta_data.set(key, value)

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()

        full_data_shape = list(in_dataset[0].get_shape())

        # Sort out input data
        in_pData[0].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

        # use this for 3D data (need to keep slice dimension)
        out_dataset = self.get_out_datasets()
        out_pData = self.get_plugin_out_datasets()

        for i in range(self.nOutput_datasets()):
            out_dataset[i].create_dataset(axis_labels=in_dataset[0],
                                          patterns=in_dataset[0],
                                          shape=tuple([x/(2**i) for x in full_data_shape]))
            out_pData[i].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 3

    def get_max_frames(self):
        return 8

    def fix_transport(self):
        return 'hdf5'
