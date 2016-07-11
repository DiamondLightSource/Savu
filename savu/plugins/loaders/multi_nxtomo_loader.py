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

from savu.plugins.base_loader import BaseLoader
from savu.plugins.loaders.nxtomo_loader import NxtomoLoader
from savu.plugins.utils import register_plugin
from savu.data.data_structures.data_type import MultipleImageKey


@register_plugin
class MultiNxtomoLoader(BaseLoader):
    """
    A class to load multiple scans in Nexus format into one dataset.

    :param file_name: The shared part of the name of each file\
        (not including .nxs). Default: None.
    :param data_path: Path to the data inside the \
        file. Default: 'entry1/tomo_entry/data/data'.
    :param stack_or_cat: Stack or concatenate the data\
        (4D and 3D respectively). Default: 'stack'.
    :param stack_or_cat_dim: Dimension to stack or concatenate. Default: 3.
    :param axis_label: New axis label, if required, in the form\
        'name.units'. Default: 'scan.number'.
    :param range: The start and end of file numbers. Default: [0, 10].
    """

    def __init__(self, name='MultiNxtomoLoader'):
        super(MultiNxtomoLoader, self).__init__(name)

    def setup(self):
        nxtomo = self._get_nxtomo()
        data_obj_list = self._get_data_objects(nxtomo)
        data_obj = self.exp.create_data_object('in_data', 'tomo')

        # dummy file
        filename = path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        stack_or_cat = self.parameters['stack_or_cat']
        dim = self.parameters['stack_or_cat_dim']
        data_obj.data = MultipleImageKey(data_obj_list, stack_or_cat, dim)
        self._set_dark_and_flat(data_obj_list, data_obj)

        if stack_or_cat == 'cat':
            nxtomo._setup_3d(data_obj)
            self._extend_axis_label_values(data_obj_list, data_obj)
        else:
            self._setup_4d(data_obj)

        print "setting the final data shape", data_obj.data.get_shape()
        data_obj.set_original_shape(data_obj.data.get_shape())
        self.set_data_reduction_params(data_obj)

    def _get_nxtomo(self):
        nxtomo = NxtomoLoader()
        nxtomo.exp = self.exp
        nxtomo._populate_default_parameters()
        return nxtomo

    def _get_data_objects(self, nxtomo):
        rrange = self.parameters['range']
        file_list = range(rrange[0], rrange[1]+1)
        file_path = copy.copy(self.exp.meta_data.get_meta_data('data_file'))
        file_name = '' if self.parameters['file_name'] is None else\
            self.parameters['file_name']

        data_obj_list = []
        for i in file_list:
            this_file = file_path + file_name + str(i) + '.nxs'
            print this_file
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
        axis_labels.insert(extra_label)

        rot = axis_labels.index('rotation_angle.degrees')
        detY = axis_labels.index('detector_y.pixel')
        detX = axis_labels.index('detector_x.pixel')
        extra = axis_labels.index(extra_label)

        data_obj.set_axis_labels(*axis_labels)

        data_obj.add_pattern('PROJECTION', core_dir=(detX, detY),
                             slice_dir=(rot, extra))
        data_obj.add_pattern('SINOGRAM', core_dir=(detX, rot),
                             slice_dir=(detY, extra))

    def _extend_axis_label_values(self, data_obj_list, data_obj):
        dim = self.parameters['stack_or_cat_dim']
        axis_name = data_obj.get_axis_labels()[dim].keys()[0].split('.')[0]

        new_values = np.zeros(data_obj.data.get_shape()[dim])
        inc = len(data_obj_list[0].meta_data.get(axis_name))

        for i in range(len(data_obj_list)):
            new_values[i*inc:i*inc+inc] = \
                data_obj_list[i].meta_data.get(axis_name)

        data_obj.meta_data.set_meta_data(axis_name, new_values)

    def _set_dark_and_flat(self, obj_list, data_obj):
        func = {'cat': np.concatenate, 'stack': np.stack}
        if self.parameters['stack_or_cat'] == 'cat':
            dark = self._combine_data(obj_list, 'dark', func['cat'])
            flat = self._combine_data(obj_list, 'flat', func['cat'])
        else:
            dark = self._combine_data(obj_list, 'dark', func['stack']).mean(0)
            flat = self._combine_data(obj_list, 'flat', func['stack']).mean(0)
        data_obj.meta_data.set_meta_data('dark', dark)
        data_obj.meta_data.set_meta_data('flat', flat)

    def _combine_data(self, obj_list, entry, function):
        array = obj_list[0].meta_data.get(entry)
        for obj in obj_list[1:]:
            array = \
                function((array, obj.meta_data.get(entry)), axis=0)
        return array

