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

import scipy as sp
import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter


@register_plugin
class OrthoSlice(BaseFilter, CpuPlugin):
    """
    A plugin to calculate the centre of rotation using the Vo Method

    :param xy_slices: which XY slices to render. Default: [100].
    :param yz_slices: which YZ slices to render. Default: [100].
    :param xz_slices: which XZ slices to render. Default: [100].
    :param file_type: File type to save as. Default: 'png'.
    """

    def __init__(self):
        super(OrthoSlice, self).__init__("OrthoSlice")

    def process_frames(self, data):
        in_dataset, out_dataset = self.get_datasets()
        fullData = in_dataset[0]

        image_path = os.path.join(self.exp.meta_data.get('out_path'), 'OrthoSlice')
        if not os.path.exists(image_path):
            os.makedirs(image_path)

        ext = self.parameters['file_type']
        in_plugin_data = self.get_plugin_in_datasets()[0]
        pos = in_plugin_data.get_current_frame_idx()[0]

        spatial_dims = list(in_dataset[0].get_data_patterns()['VOLUME_XY']['core_dims'])
        spatial_dims += list(in_dataset[0].get_data_patterns()['VOLUME_YZ']['core_dims'])
        spatial_dims += list(in_dataset[0].get_data_patterns()['VOLUME_XZ']['core_dims'])

        spatial_dims = list(set(spatial_dims))

        slice_info = [('xy_slices', 'VOLUME_XY'),
                      ('yz_slices', 'VOLUME_YZ'),
                      ('xz_slices', 'VOLUME_XZ')]

        for direction, pattern in slice_info:
            slice_to_take = [slice(0)]*len(fullData.data.shape)
            for i in spatial_dims:
                slice_to_take[i] = slice(None)
            if (pos < len(self.parameters[direction])):
                for i in fullData.get_data_patterns()[pattern]['slice_dims']:
                    if slice_to_take[i].stop == None:
                        slice_pos = self.parameters[direction][pos]
                        slice_to_take[i] = slice(slice_pos, slice_pos+1, 1)
                image_data = fullData.data[slice_to_take[0], slice_to_take[1] ,slice_to_take[2]].squeeze()
                filename = '%s_%03i.%s' % (pattern, pos, ext)
                sp.misc.imsave(os.path.join(image_path, filename), image_data)
            else:
                pos -= len(self.parameters['xy_slices'])

        #TODO repeat for others

        return [np.array([pos])]


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

        self.orig_full_shape = in_dataset[0].get_shape()

        number_of_images = len(self.parameters['xy_slices'])
        number_of_images += len(self.parameters['yz_slices'])
        number_of_images += len(self.parameters['xz_slices'])

        # generate a fake slicelist to get paralel threads
        # FIXME this is a bit of a hack
        preview_slices = [str(number_of_images)]
        for i in range(len(self.orig_full_shape)-1):
            preview_slices.append('1')

        preview_slices = '['+','.join(preview_slices)+']'
        self.set_preview(in_dataset[0], preview_slices)

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_XZ', self.get_max_frames())
        # copy all required information from in_dataset[0]
        fullData = in_dataset[0]

        slice_dirs = np.array(in_dataset[0].get_slice_dimensions())
        new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 1)
        self.orig_shape = \
            (np.prod(np.array(self.orig_full_shape)[slice_dirs]), 1)

        out_dataset[0].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True,
                                      transport='hdf5')

        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))

        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())

        self.exp.log(self.name + " End")

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'

    def fix_transport(self):
        return 'hdf5'
