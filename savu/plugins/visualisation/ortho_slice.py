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
import logging

import scipy.misc

import matplotlib.pyplot as plt

from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)


@register_plugin
class OrthoSlice(Plugin, CpuPlugin):
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
        super(OrthoSlice, self).__init__("OrthoSlice")

    def pre_process(self):
        self.image_path = \
            os.path.join(self.exp.meta_data.get('out_path'), 'OrthoSlice')
        if self.exp.meta_data.get('process') == 0:
            if not os.path.exists(self.image_path):
                os.makedirs(self.image_path)

    def process_frames(self, data):
        self.exp.log("XXXX Starting to run process_frames in Orthoslice")
        print("XXXX Starting to run process_frames in Orthoslice")

        in_dataset = self.get_in_datasets()

        fullData = in_dataset[0]

        ext = self.parameters['file_type']
        in_plugin_data = self.get_plugin_in_datasets()[0]
        pos = in_plugin_data.get_current_frame_idx()

        self.exp.log("frame position is %s" % (str(pos)))

        slice_info = [('xy_slices', 'VOLUME_XY'),
                      ('yz_slices', 'VOLUME_YZ'),
                      ('xz_slices', 'VOLUME_XZ')]

        colourmap = plt.get_cmap(self.parameters['colourmap'])

        # Set up the output list
        output_slices = []

        for direction, pattern in slice_info:
            # build the slice list
            slice_to_take = [slice(0)]*len(fullData.data.shape)

            # Fix the main slice dimentions that are outside the spatial dimentions
            slice_count = 0
            for i in list(self.slice_dims):
                slice_to_take[i] = slice(pos[slice_count], pos[slice_count]+1, 1)
                slice_count += 1

            # set all the spatial dimentions to get everything
            for i in list(self.spatial_dims):
                slice_to_take[i] = slice(None)

            # set the slice in the direction
            slice_value = self.parameters[direction]
            slice_to_take[self.axis_loc[pattern]] = slice(slice_value,
                                                          slice_value+1, 1)

            print(("Final slice is : %s of %s" % (str(slice_to_take),
                                                 str(fullData.data.shape))))
            self.exp.log("Final slice is : %s of %s" % (str(slice_to_take),
                                                        str(fullData.data.shape)))

            # now retreive the data from the fulldata given the current slice
            ortho_data = fullData.data[tuple(slice_to_take)].squeeze()
            output_slices.append(ortho_data)

            if ext is not 'None':
                image_data = ortho_data - ortho_data.min()
                image_data /= image_data.max()
                image_data = colourmap(image_data, bytes=True)

                filename = '%s_%03i_%s.%s' % (pattern, slice_value,
                                              str(pos), ext)
                self.exp.log("image-data shape is %s and filename is '%s'" %
                             (str(image_data.shape), filename))

                scipy.misc.imsave(os.path.join(self.image_path, filename), image_data)

        return output_slices


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

        pattern = ['VOLUME_XY', 'VOLUME_YZ', 'VOLUME_XZ']
        fixed_axis = ['voxel_z', 'voxel_x', 'voxel_y']

        self.spatial_dims = []
        self.axis_loc = {}
        for patt, axis in zip(pattern, fixed_axis):
            self.axis_loc[patt] = in_dataset[0].get_data_dimension_by_axis_label(axis)
            self.spatial_dims.append(self.axis_loc[patt])

        self.all_dims = set(range(len(full_data_shape)))
        self.slice_dims = self.all_dims.difference(set(self.spatial_dims))

        self.exp.log("Axis Locations are %s" % (str(self.axis_loc)))

        # Sort out input data
        in_pData[0].plugin_data_setup('VOLUME_XY', self.get_max_frames())
        fixed_dim = in_dataset[0].get_data_dimension_by_axis_label('voxel_z')
        preview = [':']*len(in_dataset[0].get_shape())
        preview[fixed_dim] = str(0)
        self.set_preview(in_dataset[0], preview)

        # use this for 3D data (need to keep slice dimension)
        out_dataset = self.get_out_datasets()
        out_pData = self.get_plugin_out_datasets()

        for i, (p, axis) in enumerate(zip(pattern, fixed_axis)):
            fixed_dim = in_dataset[0].get_data_dimension_by_axis_label(axis)
            shape, patterns, labels = self._get_data_params(
                    in_dataset[0], full_data_shape, fixed_dim, p)
            out_dataset[i].create_dataset(axis_labels=labels,
                                          shape=tuple(shape),
                                          patterns=patterns)
            out_pData[i].plugin_data_setup(p, self.get_max_frames())

    def _get_data_params(self, data, full_data_shape, fixed_dim, p):
        shape = copy.copy(full_data_shape)
        if self.slice_dims:
            # for > 3D data
            del shape[fixed_dim]
            pattern = {data: ['%s.%i'%(p, fixed_dim)]}
            labels = {data: [str(fixed_dim)]}
        else:
            # for 3D data
            shape[fixed_dim] = 1
            pattern = {data: [p]}
            labels = data
        return shape, pattern, labels

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 3

    def get_max_frames(self):
        return 'single'

    def fix_transport(self):
        return 'hdf5'
