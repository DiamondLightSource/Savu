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
.. module:: multi_nxtomo_loader
   :platform: Unix
   :synopsis: A class for loading multiple standard tomography scans.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import copy
import h5py
import tempfile
from os import path
import numpy as np

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.loaders.full_field_loaders.nxtomo_loader import NxtomoLoader
from savu.plugins.utils import register_plugin
from savu.data.data_structures.data_types.stitch_data import StitchData


@register_plugin
class MultiNxtomoLoader(BaseLoader):


    def __init__(self, name='MultiNxtomoLoader'):
        super(MultiNxtomoLoader, self).__init__(name)

    def setup(self):
        nxtomo = self._get_nxtomo()
        preview = self.parameters['preview']
        stitch_dim = self.parameters['stack_or_cat_dim']
        nxtomo.parameters['preview'] = \
            [x for i, x in enumerate(preview) if i != stitch_dim]
        data_obj_list = self._get_data_objects(nxtomo)
        data_obj = \
            self.exp.create_data_object('in_data', self.parameters['name'])

        # dummy file
        filename = path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        stack_or_cat = self.parameters['stack_or_cat']
        data_obj.data = StitchData(data_obj_list, stack_or_cat, stitch_dim)

        if stack_or_cat == 'cat':
            nxtomo._setup_3d(data_obj)
            self._extend_axis_label_values(data_obj_list, data_obj)
        else:
            self._setup_4d(data_obj)

        data_obj.set_original_shape(data_obj.data.get_shape())
        self.set_data_reduction_params(data_obj)
        # Must do this here after preview has been applied
        if stack_or_cat == 'stack':
            self._set_nD_rotation_angle(data_obj_list, data_obj)
    
    def _get_nxtomo(self):
        nxtomo = NxtomoLoader()
        nxtomo.exp = self.exp
    
        # update nxtomo parameters with any common keys
        shared_keys = set(nxtomo.parameters.keys()).intersection(
            set(self.parameters.keys()))
        for key in shared_keys:
            nxtomo.parameters[key] = self.parameters[key]
        return nxtomo    

    def _get_data_objects(self, nxtomo):
        rrange = self.parameters['range']
        file_list = list(range(rrange[0], rrange[1]+1))
        file_path = copy.copy(self.exp.meta_data.get('data_file'))
        file_name = '' if self.parameters['file_name'] is None else\
            self.parameters['file_name']

        data_obj_list = []
        for i in file_list:
            this_file = file_path + file_name + str(i) + '.nxs'
            self.exp.meta_data.set('data_file', this_file)
            nxtomo.setup()
            data_obj_list.append(self.exp.index['in_data']['tomo'])
            self.exp.index['in_data'] = {}

        self.exp.meta_data.set('data_file', file_path)
        return data_obj_list

    def _setup_4d(self, data_obj):
        axis_labels = \
            ['rotation_angle.degrees', 'detector_y.pixel', 'detector_x.pixel']

        extra_label = self.parameters['axis_label']
        axis_labels.append(extra_label)

        rot = axis_labels.index('rotation_angle.degrees')
        detY = axis_labels.index('detector_y.pixel')
        detX = axis_labels.index('detector_x.pixel')
        extra = axis_labels.index(extra_label)

        data_obj.set_axis_labels(*axis_labels)

        data_obj.add_pattern('PROJECTION', core_dims=(detX, detY),
                             slice_dims=(rot, extra))
        data_obj.add_pattern('SINOGRAM', core_dims=(detX, rot),
                             slice_dims=(detY, extra))

        data_obj.add_pattern('PROJECTION_STACK', core_dims=(detX, detY),
                             slice_dims=(extra, rot))
        data_obj.add_pattern('SINOGRAM_STACK', core_dims=(detX, rot),
                             slice_dims=(extra, detY))

    def _extend_axis_label_values(self, data_obj_list, data_obj):
        dim = self.parameters['stack_or_cat_dim']
        axis_name = list(data_obj.get_axis_labels()[dim].keys())[0].split('.')[0]

        new_values = np.zeros(data_obj.data.get_shape()[dim])
        inc = len(data_obj_list[0].meta_data.get(axis_name))

        for i in range(len(data_obj_list)):
            new_values[i*inc:i*inc+inc] = \
                data_obj_list[i].meta_data.get(axis_name)

        data_obj.meta_data.set(axis_name, new_values)

    def _set_nD_rotation_angle(self, data_obj_list, data_obj):
        shape = data_obj.get_shape()
        rot_dim_len = data_obj.get_shape()[
            data_obj.get_data_dimension_by_axis_label('rotation_angle')]
        new_values = np.zeros([rot_dim_len, len(data_obj_list)])
        for i in range(len(data_obj_list)):
            new_values[:, i] = \
                data_obj_list[i].meta_data.get('rotation_angle')
        data_obj.meta_data.set('rotation_angle', new_values)


    def get_dark_flat_slice_list(self, data_obj):
        slice_list = data_obj._preview._get_preview_slice_list()
        detX_dim = data_obj.get_data_dimension_by_axis_label('detector_x')
        detY_dim = data_obj.get_data_dimension_by_axis_label('detector_y')
        dims = list(set([detX_dim, detY_dim]))
        new_slice_list = []
        for d in dims:
            new_slice_list.append(slice_list[d])
        return new_slice_list
