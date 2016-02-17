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
.. module:: tomography_loader
   :platform: Unix
   :synopsis: A class for loading tomography data using the standard loaders
   library.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging

import savu.data.data_structures as ds
from savu.plugins.base_loader import BaseLoader
import savu.data.data_structures as ds

from savu.plugins.utils import register_plugin


@register_plugin
class SavuLoader(BaseLoader):
    """
    A class to load Savu output data from a hdf5 file
    :param data_path: Path to the \
        data. Default: 'entry/final_result_tomo/data'.
    :param name: Name associated with the data set. Default: 'tomo'.
    """

    def __init__(self, name='SavuLoader'):
        super(SavuLoader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', self.parameters['name'])

        expInfo = exp.meta_data

        data_obj.backing_file = \
            h5py.File(expInfo.get_meta_data("data_file"), 'r')

        data_path = self.parameters['data_path']
        entry_path = '/'.join(data_path.split('/')[:-1])
        data_obj.data = data_obj.backing_file[data_path]

        self.set_axis_labels(data_obj, entry_path)
        self.add_patterns(data_obj, entry_path)
        self.add_meta_data(data_obj, entry_path)

        data_obj.set_shape(data_obj.data.shape)
        self.set_data_reduction_params(data_obj)

    def set_axis_labels(self, data, entry):
        # set axis labels
        axes = data.backing_file[entry].attrs['axes']
        axis_labels = []
        for axis in axes:
            units = data.backing_file[entry + '/' + axis].attrs['units']
            axis_labels.append(axis + '.' + units)
        data.set_axis_labels(*axis_labels)

    def add_patterns(self, data, entry):
        pattern_list = data.backing_file[entry + '/patterns'].keys()
        for pattern in pattern_list:
            pattern = pattern.encode('ascii')
            pEntry = entry + '/patterns/' + pattern
            core_dir = tuple(data.backing_file[pEntry + '/core_dir'][...])
            slice_dir = tuple(data.backing_file[pEntry + '/slice_dir'][...])
            data.add_pattern(pattern, core_dir=core_dir, slice_dir=slice_dir)

    def add_meta_data(self, data, entry):
        meta_data_list = data.backing_file[entry + '/meta_data'].keys()
        for mData_name in meta_data_list:
            mData_name = mData_name.encode('ascii')
            mEntry = entry + '/meta_data/' + mData_name
            mData = data.backing_file[mEntry + '/' + mData_name]
            if mData_name is 'image_key':
                self.set_image_key(data, mData)
            else:
                data.meta_data.set_meta_data(mData_name, mData[...])

    def set_image_key(self, data, mData):
        ds.TomoRaw(data)
        data.get_tomo_raw().set_image_key(mData[...])
