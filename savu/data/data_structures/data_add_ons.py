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
   :synopsis: A module containing add_on classes, which have instances
   encapsulated within the Data class.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import warnings


class TomoRaw(object):
    """ A class associated with a dataset that has an image key.  It performs
    operations on the image_key.
    """

    def __init__(self, data_obj):
        self.data_obj = data_obj
        self.data_obj._set_tomo_raw(self)
        self.image_key_slice = None
        self.frame_list = []

    def _remove_image_key(self, copy_obj, image_key=0):
        """ Reduce the shape of a dataset to be only the size of the data and
        remove the TomoRaw instance encapsulated inside the Data object

        :params Data copy_obj: A Data object with an image key
        :keyword int image_key: The image_key data index (assumed to be 0 for
            now)
        """
        # the image key should be the index of the data, not necessarily zero.
        if image_key is 0:
            if copy_obj.tomo_raw_obj:
                self.data_obj.set_shape(
                    copy_obj.get_tomo_raw().__remove_dark_and_flat())
                self.data_obj._clear_tomo_raw()

    def set_image_key(self, image_key):
        """ Set the image_key in the data meta_data dictionary

        :params np.ndarray image_key: The image key
        """
        self.data_obj.meta_data.set_meta_data('image_key', image_key)

    def get_image_key(self):
        """ Get the image key

        :returns: The image key array
        :rtype: np.ndarray
        """
        return self.data_obj.meta_data.get_meta_data('image_key')

    def __get_image_key_slice(self):
        return self.image_key_slice

    def __remove_dark_and_flat(self):
        if self.get_image_key() is not None:
            shape = self.data_obj.get_shape()
            image_key = self.get_image_key()
            new_shape = shape[0] - len(image_key[image_key != 0])
            return (new_shape, shape[1], shape[2])
        else:
            logging.warn("Error in remove_dark_and_flat(): No image_key found")
            shape = self.get_shape()
            return (shape, shape[1], shape[2])

    def _get_frame_raw(self, slice_list):
        pattern = self.data_obj._get_plugin_data()._get_pattern_name()
        image_slice = self.__get_image_key_slice()
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
    """ A class that organises padding of the data. An instance of Padding can
    be associated with a Data object in a plugin that inherits from BaseFilter,
    inside :meth:`savu.plugins.base_filter.BaseFilter.set_filter_padding`
    """

    def __init__(self, pattern):
        self.padding_dirs = {}
        self.pattern_name = pattern.keys()[0]
        self.pattern = pattern[self.pattern_name]
        self.dims = self.__set_dims()

    def __set_dims(self):
        dims = []
        for key in self.pattern.keys():
            temp = self.pattern[key]
            for dim in (temp,) if isinstance(temp, int) else temp:
                dims.append(int(dim))
        dims = list(set(dims))
        return dims

    def pad_frame_edges(self, padding):
        """ Pad the edges of a frame of data (i.e pad in the core dimensions)

        :param int padding: The pad amount
        """
        core_dirs = self.pattern['core_dir']
        for core in core_dirs:
            self.__pad_direction([core, padding])

    def pad_multi_frames(self, padding):
        """ Add extra frames before and after the current frame of data (i.e
        pad in the fastest changing slice dimension).

        :param int padding: The pad amount
        """
        try:
            main_dir = self.pattern['main_dir']
        except KeyError:
            raise Exception('There is no main_dir associated with this '
                            'pattern')
        self.__pad_direction([main_dir, padding])

    def pad_directions(self, pad_list):
        """ Pad multiple, individually specified, dimensions.

        :param list(dict) pad_list: A list of single entry dictionaries, \
            key = dimension, value = pad amount.
        """
        for entry in pad_list:
            for key, value in entry.iteritems():
                self.__pad_direction([key, value])

    def __pad_direction(self, pad_list):
        """ Pad the data in a specified dimension.

        :param list pad_list: A list (len = 2), where the first element is the
        dimension to pad and the second element is the pad amount.
        """
        pdir = pad_list[0]
        padding = pad_list[1]
        if pdir not in self.dims:
            warnings.warn('Dimension ' + str(pdir) + ' is not associated '
                          ' with the pattern ' + self.pattern_name, +
                          '. IGNORING!')
        elif pdir in self.padding_dirs:
            warnings.warn('Padding.add_dir(): The direction ' + str(pdir) +
                          ' has already been added to the padding list.')
            self.padding_dirs[pdir] += padding
        else:
            self.padding_dirs[pdir] = padding

    def _get_padding_directions(self):
        """ Get padding directions.

        :returns: padding dictionary
        :rtype: dict
        """
        return self.padding_dirs


class DataMapping(object):
    """ A class providing helper functions to multi-modal loaders.
    """

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
