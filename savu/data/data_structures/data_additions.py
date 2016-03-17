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
.. module:: data_additions
   :platform: Unix
   :synopsis: Contains the Data class and all the data structures from which \
   Data can inherit.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import warnings
import numpy as np


class TomoRaw(object):

    def __init__(self, data_obj):
        self.data_obj = data_obj
        self.data_obj._set_tomo_raw(self)
        self.image_key_slice = None
        self.frame_list = []

    def select_image_key(self, **kwargs):
        image_key = kwargs['image_key']
        self.data_obj._get_plugin_data().selected_data = True
        self.set_image_key_slice(image_key)

    def remove_image_key(self, copy_obj, **kwargs):
        image_key = kwargs.get('image_key', 0)
        if image_key is 0:
            if copy_obj.tomo_raw_obj:
                self.data_obj.set_shape(
                    copy_obj.get_tomo_raw().remove_dark_and_flat())
                self.data_obj._clear_tomo_raw()

    def get_raw_flag(self):
        return self.raw_flag

    def set_image_key(self, image_key):
        self.data_obj.meta_data.set_meta_data('image_key', image_key)

    def get_image_key(self):
        return self.data_obj.meta_data.get_meta_data('image_key')

    def set_frame_list(self, start, end):
        self.frame_list = [start, end]

    def set_image_key_slice(self, value):
        image_key_bool = self.get_image_key() == value
        image_key_index = np.where(image_key_bool)[0]
        start = image_key_index[0]
        end = image_key_index[-1]
        self.set_frame_list(start, end)
        self.image_key_slice = slice(start, end + 1, 1)

    def get_image_key_slice(self):
        return self.image_key_slice

    def remove_dark_and_flat(self):
        if self.get_image_key() is not None:
            shape = self.data_obj.get_shape()
            image_key = self.get_image_key()
            new_shape = shape[0] - len(image_key[image_key != 0])
            return (new_shape, shape[1], shape[2])
        else:
            logging.warn("Error in remove_dark_and_flat(): No image_key found")
            shape = self.get_shape()
            return (shape, shape[1], shape[2])

    def get_frame_raw(self, slice_list):
        pattern = self.data_obj._get_plugin_data().get_pattern_name()
        image_slice = self.get_image_key_slice()
        new_slice_list = []
        if pattern is "SINOGRAM":
            for sl in slice_list:
                sl = list(sl)
                sl[0] = image_slice
                sl = tuple(sl)
                new_slice_list.append(sl)
        elif pattern is "PROJECTION":
            new_slice_list = slice_list[self.frame_list[0]:self.frame_list[1]]
        else:
            raise Exception("The pattern", pattern, " is not recognized \
                             by", self.__name__)

        return new_slice_list


class Padding(object):

    def __init__(self, pattern):
        self.padding_dirs = {}
        self.pattern_name = pattern.keys()[0]
        self.pattern = pattern[self.pattern_name]
        self.dims = self.set_dims()

    def set_dims(self):
        dims = []
        for key in self.pattern.keys():
            temp = self.pattern[key]
            for dim in (temp,) if type(temp) is int else temp:
                dims.append(int(dim))
        dims = list(set(dims))
        return dims

    def pad_frame_edges(self, padding):
        core_dirs = self.pattern['core_dir']
        for core in core_dirs:
            self.pad_direction([core, padding])

    def pad_multi_frames(self, padding):
        try:
            main_dir = self.pattern['main_dir']
        except KeyError:
            raise Exception('There is no main_dir associated with this '
                            'pattern')
        self.pad_direction([main_dir, padding])

    def pad_direction(self, pad_list):
        pdir = pad_list[0]
        padding = pad_list[1]
        if pdir not in self.dims:
            warnings.warn('Dimension ' + str(pdir) + ' is not associated '
                          ' with the pattern ' + self.pattern_name, +
                          '. IGNORING!')
        elif pdir in self.padding_dirs:
            warnings.warn('Padding.add_dir(): The direction ' + str(pdir) +
                          ' has already been added to the padding list.')
        else:
            self.padding_dirs[pdir] = padding

    def get_padding_directions(self):
        return self.padding_dirs


class DataMapping(object):

    def __init__(self):
        self._is_tomo = None
        self._is_map = None
        self._motors = None
        self._motor_type = None
        self._axes = None

    def set_motors(self, motors):
        self.motors = motors

    def get_motors(self):
        return self.motors

    def set_motor_type(self, motor_type):
        self.motor_type = motor_type

    def get_motor_type(self):
        return self.motor_type

    def set_axes(self, axes):
        self.axes = axes

    def get_axes(self):
        return self.axes

    def check_is_map(self, proj_dir):
        pattern = []
        if self.get_meta_data("is_map"):
            ovs = []
            for i in self.get_shape():
                if i != proj_dir[0]:
                    if i != proj_dir[1]:
                        ovs.append(i)
            pattern = {"PROJECTION", {'core_dir': proj_dir, 'slice_dir': ovs}}
        return pattern

    def check_is_tomo(self, proj_dir, rotation):
        pattern = []
        if self.get_meta_data("is_tomo"):
            ovs = []
            for i in self.get_shape():
                if i != rotation:
                    if i != proj_dir[1]:
                        ovs.append(i)
            pattern = {"SINOGRAM", {'core_dir': (rotation, proj_dir[-1]),
                                    'slice_dir': ovs}}
        return pattern
