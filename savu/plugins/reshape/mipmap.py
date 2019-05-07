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
.. module:: mipmaping plugin (a pyramid-like data downampling)
   :platform: Unix
   :synopsis:A plugin to downsample multidimensional data 
.. moduleauthor:: Mark Basham & Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.driver.cpu_plugin import CpuPlugin

import logging
import math
import skimage.measure as skim
import numpy as np
from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)


@register_plugin
class Mipmap(Plugin, CpuPlugin):
    """
    A plugin to downsample multidimensional data (scales of 2 and 4 are generated),\
    Mipmap0 is the original size data, Mipmap1 is scaled down by 2 and Mipmap2 by 4

    :u*param mode: One of 'mean', 'median', 'min', 'max'. Default: 'mean'.
    :param out_datasets: Default out dataset names. Default: ['Mipmap0', 'Mipmap1', 'Mipmap2']
    """

    def __init__(self):
        super(Mipmap, self).__init__("Mipmap")

    def pre_process(self):
        pass

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

        in_dataset = self.get_in_datasets()
        out_datasets = self.get_out_datasets()

        fullData = in_dataset[0]

        #out0 = out_datasets[0]
        #out1 = out_datasets[1]
        #out2 = out_datasets[2]

#       ext = self.parameters['file_type']
        in_plugin_data = self.get_plugin_in_datasets()[0]
        pos = np.unique(in_plugin_data.get_current_frame_idx())

        self.exp.log("frame position is %s" % (str(pos)))
        """
        # a list of tuples
        mipmap_info = [(out0, data[0], 1),
                       (out1, skim.block_reduce(data[0], (2, 2, 2), sampler), 2),
                       (out2, skim.block_reduce(data[0], (4, 4, 4), sampler), 4)]
        """
        """
        mipmap_info = []
        data_mipmap0 = tuple([out_datasets[0], data[0], 1])
        mipmap_info.append(data_mipmap0)
        downsample1 = skim.block_reduce(data[0], (2, 2, 2), sampler)
        data_mipmap1 = tuple([out_datasets[1], downsample1, 2])
        mipmap_info.append(data_mipmap1)
        downsample2 = skim.block_reduce(downsample1, (2, 2, 2), sampler)
        data_mipmap2 = tuple([out_datasets[2], downsample2, 4])
        mipmap_info.append(data_mipmap2)
        """
        
        # Mipmapped layers appended in the loop 
        mipmap_info = []
        data_mipmap0 = tuple([out_datasets[0], data[0], 1])
        mipmap_info.append(data_mipmap0)
        inputMap = data[0]
        counter = 2
        for i in range(1,3):
            downsample = skim.block_reduce(inputMap, (2, 2, 2), sampler)
            data_mipmap = tuple([out_datasets[i], downsample, counter])
            mipmap_info.append(data_mipmap)
            inputMap = np.copy(downsample)
            counter = counter + 2
        
        # Set up the output list
        #output_slices = []
        # mipmap levels
        for output_dataset, data_block, size in mipmap_info:
            # build the slice list
            slice_to_take = [slice(None)]*len(fullData.data.shape)

            mapped_slice = (pos/size)[size-1::size]

            if mapped_slice.shape[0] > 0:
                slice_to_take[in_plugin_data.get_slice_dimension()] = mapped_slice
                output_dataset.data[tuple(slice_to_take)] = data_block[:, 0:mapped_slice.shape[0],:]

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
                                          shape=tuple([int(math.ceil(x/(2**i))) for x in full_data_shape]))
            out_pData[i].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 3

    def get_max_frames(self):
        return 8

    def fix_transport(self):
        return 'hdf5'
