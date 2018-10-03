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
.. module:: ortho_slice
   :platform: Unix
   :synopsis: A plugin render some slices from a volume and save them as images
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.driver.cpu_plugin import CpuPlugin

import os
import copy

import scipy as sp
import numpy as np

import matplotlib.pyplot as plt

from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin
from savu.plugins.filters.base_filter import BaseFilter


@register_plugin
class OrthoSlice(Plugin, CpuPlugin):
    """
    A plugin to calculate the centre of rotation using the Vo Method

    :u*param xy_slices: which XY slices to render. Default: [100].
    :u*param yz_slices: which YZ slices to render. Default: [100].
    :u*param xz_slices: which XZ slices to render. Default: [100].
    :u*param file_type: File type to save as. Default: 'png'.
    :u*param colourmap: Colour scheme to apply to the image. Default: 'magma'.
    :param out_datasets: Default out dataset names. Default: ['XY', 'YZ', 'XZ'].
    
    """

    def __init__(self):
        super(OrthoSlice, self).__init__("OrthoSlice")

    def pre_process(self):
        BaseFilter.pre_process(self)

    def process_frames(self, data):
        
        data[0] 
        
        in_dataset = self.get_in_datasets()
        
        fullData = in_dataset[0]

        image_path = os.path.join(self.exp.meta_data.get('out_path'), 'OrthoSlice')
        if not os.path.exists(image_path):
            os.makedirs(image_path)

        ext = self.parameters['file_type']
        in_plugin_data = self.get_plugin_in_datasets()[0]
        pos = in_plugin_data.get_current_frame_idx()[0]

        slice_info = [('xy_slices', 'VOLUME_XY'),
                      ('yz_slices', 'VOLUME_YZ'),
                      ('xz_slices', 'VOLUME_XZ')]


        #TODO this can probably be moved somewhere better
        colourmap = plt.get_cmap(self.parameters['colourmap'])
        

        for direction, pattern in slice_info:
            slice_to_take = [slice(0)]*len(fullData.data.shape)
            for i in list(self.spatial_dims):
                slice_to_take[i] = slice(None)
            if (pos < len(self.parameters[direction])):
                for i in fullData.get_data_patterns()[pattern]['slice_dims']:
                    if slice_to_take[i].stop == None:
                        slice_pos = self.parameters[direction][pos]
                        slice_to_take[i] = slice(slice_pos, slice_pos+1, 1)
                image_data = fullData.data[slice_to_take[0],
                                           slice_to_take[1],
                                           slice_to_take[2]].squeeze()

                image_data -= image_data.min()
                image_data /= image_data.max()
                image_data = colourmap(image_data, bytes=True)

                filename = '%s_%03i.%s' % (pattern, pos, ext)

                sp.misc.imsave(os.path.join(image_path, filename), image_data)
            else:
                pos -= len(self.parameters['xy_slices'])

        #TODO repeat for others

        return [data[0], yz_data, xz_data]


    def populate_meta_data(self, key, value):
        datasets = self.parameters['datasets_to_populate']
        in_meta_data = self.get_in_meta_data()[0]
        in_meta_data.set(key, value)
        for name in datasets:
            self.exp.index['in_data'][name].meta_data.set(key, value)

    def setup(self):

        self.exp.log(self.name + " Start")

        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        full_data_shape = list(in_dataset[0].get_shape())

        spatial_dims = list(in_dataset[0].get_data_patterns()['VOLUME_XY']['core_dims'])
        spatial_dims += list(in_dataset[0].get_data_patterns()['VOLUME_YZ']['core_dims'])
        spatial_dims += list(in_dataset[0].get_data_patterns()['VOLUME_XZ']['core_dims'])

        self.spatial_dims = set(spatial_dims)

        in_pData, out_pData = self.get_plugin_datasets()

        # Sort out input data
        in_pData[0].plugin_data_setup('VOLUME_XY', self.get_max_frames())
        fixed_dim = list(self.spatial_dims.difference(set(in_pData[0].get_core_dimensions())))
        in_pData[0].set_fixed_dimensions(fixed_dim,[self.parameters['xy_slices']])


        # Create output datsets
        reduced_shape = copy.copy(full_data_shape)
        del reduced_shape[fixed_dim[0]]
        out_dataset[0].create_dataset(axis_labels={in_dataset[0]: [str(fixed_dim[0])] },
                                      shape=tuple(reduced_shape),
                                      patterns={in_dataset[0]: ['VOLUME_XY.%i'%fixed_dim[0]]})
        out_pData[0].plugin_data_setup('VOLUME_XY', self.get_max_frames())

        # Sort out dataset 1
        fixed_dim = list(self.spatial_dims.difference(set(in_pData[0].get_core_dimensions())))
        reduced_shape = copy.copy(full_data_shape)
        del reduced_shape[fixed_dim[0]]
        out_dataset[1].create_dataset(axis_labels={in_dataset[0]: [str(fixed_dim[0])] },
                                      shape=tuple(reduced_shape),
                                      patterns={in_dataset[0]: ['VOLUME_YZ.%i'%fixed_dim[0]]})
        out_pData[1].plugin_data_setup('VOLUME_YZ', self.get_max_frames())

        # Sort out dataset 2
        fixed_dim = list(self.spatial_dims.difference(set(in_pData[0].get_core_dimensions())))
        reduced_shape = copy.copy(full_data_shape)
        del reduced_shape[fixed_dim[0]]
        out_dataset[2].create_dataset(axis_labels={in_dataset[0]: [str(fixed_dim[0])] },
                                      shape=tuple(reduced_shape),
                                      patterns={in_dataset[0]: ['VOLUME_XZ.%i'%fixed_dim[0]]})
        out_pData[2].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

        self.exp.log(self.name + " End")

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 3

    def get_max_frames(self):
        return 'single'

    def fix_transport(self):
        return 'hdf5'
