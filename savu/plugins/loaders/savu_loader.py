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
.. module:: savu_loader
   :platform: Unix
   :synopsis: A class for loading savu output data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import numpy as np

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
from savu.data.data_structures.data_types.data_plus_darks_and_flats \
    import ImageKey


@register_plugin
class SavuLoader(BaseLoader):
    """
    A class to load Savu output data from a hdf5 file
    :param data_path: Path to the \
        data. Default: '1-TimeseriesFieldCorrections-tomo/data'.
    :param name: Name associated with the data set. Default: 'tomo'.
    :param image_key: Specify position of darks and flats (in that order) \
    in the data e.g. [[0, 1], [2, 3]]. Default: None.
    :param angles: Override angles. Default: None.
    """

    def __init__(self, name='SavuLoader'):
        super(SavuLoader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', self.parameters['name'])

        expInfo = exp.meta_data

        data_obj.backing_file = \
            h5py.File(expInfo.get("data_file"), 'r')

        data_path = self.parameters['data_path']
        entry_path = '/'.join(data_path.split('/')[:-1])
        data_obj.data = data_obj.backing_file[data_path]

        self.__set_axis_labels(data_obj, entry_path)
        self.__add_patterns(data_obj, entry_path)
        self.__add_meta_data(data_obj, entry_path)

        if self.parameters['image_key']:
            self.__set_image_key(data_obj)

        angles = None
        if self.parameters['angles']:
            exec("angles = " + self.parameters['angles'])
            data_obj.meta_data.set("rotation_angle", angles)

        data_obj.set_shape(data_obj.data.shape)
        self.set_data_reduction_params(data_obj)
        if isinstance(data_obj.data, ImageKey):
            data_obj.data._set_dark_and_flat()

    def __set_axis_labels(self, data, entry):
        # set axis labels
        axes = data.backing_file[entry].attrs['axes']
        axis_labels = []
        for axis in axes:
            units = data.backing_file[entry + '/' + axis].attrs['units']
            axis_labels.append(axis + '.' + units)
        data.set_axis_labels(*axis_labels)

    def __add_patterns(self, data, entry):
        pattern_list = data.backing_file[entry + '/patterns'].keys()
        for pattern in pattern_list:
            pattern = pattern.encode('ascii')
            pEntry = entry + '/patterns/' + pattern
            try:
                core_dims = data.backing_file[pEntry + '/core_dims'][...]
                slice_dims = data.backing_file[pEntry + '/slice_dims'][...]
            except:
                core_dims = data.backing_file[pEntry + '/core_dir'][...]
                slice_dims = data.backing_file[pEntry + '/slice_dir'][...]

            data.add_pattern(pattern, core_dims=tuple(core_dims),
                             slice_dims=tuple(slice_dims))

    def __add_meta_data(self, data, entry):
        meta_data_list = data.backing_file[entry + '/meta_data'].keys()
        for mData_name in meta_data_list:
            mData_name = mData_name.encode('ascii')
            mEntry = entry + '/meta_data/' + mData_name
            mData = data.backing_file[mEntry + '/' + mData_name]
            data.meta_data.set(mData_name, mData[...])

    def __set_image_key(self, data_obj):
        proj_slice = \
            data_obj.get_data_patterns()['PROJECTION']['slice_dims'][0]
        image_key = np.zeros(data_obj.data.shape[proj_slice], dtype=int)
        dark, flat = self.parameters['image_key']
        image_key[np.array(dark)] = 2
        image_key[np.array(flat)] = 1

        data_obj.data = ImageKey(data_obj, image_key, 0)
