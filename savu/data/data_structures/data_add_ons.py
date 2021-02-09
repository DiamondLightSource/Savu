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
   :synopsis: A module containing add_on classes, which have instances \
       encapsulated within the Data class.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import savu.data.data_structures.data_notes as notes
from savu.core.utils import docstring_parameter


class Padding(object):
    """ A class that organises padding of the data. An instance of Padding can
    be associated with a Data object in a plugin that inherits from BaseFilter,
    inside :meth:`savu.plugins.base_filter.BaseFilter.set_filter_padding`
    """

    def __init__(self, pData):
        self._pData = pData
        self.mtp = pData._get_max_frames_process()
        self.padding_dirs = {}
        self.pad_dict = None
        self.dims = None
        self.pattern_name = list(pData.get_pattern().keys())[0]
        self.pattern = pData.get_pattern()[self.pattern_name]
        self.dims = self.__set_dims()
        self.mode = 'edge'

    def __set_dims(self):
        dims = []
        core_dir = self.pattern['core_dims']
        slice_dir = self.pattern['slice_dims']
        for dim in range(len(core_dir + slice_dir)):
            self.padding_dirs[dim] = {'before': 0, 'after': 0}
        return dims

    def pad_mode(self, mode):
        self.mode = mode

    def pad_frame_edges(self, padding):
        """ Pad all the edges of a frame of data with the same pad amount
        (i.e pad in the core dimensions).

        :param int padding: The pad amount
        """
        core_dirs = self.pattern['core_dims']
        for core in core_dirs:
            self._pad_direction(str(core) + '.' + str(padding))

    def pad_multi_frames(self, padding):
        """ Add extra frames before and after the current frame of data (i.e
        pad in the fastest changing slice dimension).

        :param int padding: The pad amount
        """
        sdir = self.pattern['slice_dims'][0]
        self._pad_direction(str(sdir) + '.' + str(padding))

    @docstring_parameter(notes._padding.__doc__)
    def pad_directions(self, pad_list):
        """ Pad multiple, individually specified, dimensions.

        :param list(dict) pad_list: A list of strings of the form 'dim.pad',\
        'dim.after.pad' or 'dim.before.pad'
        {0}

        """
        for entry in pad_list:
            self._pad_direction(entry)

    @docstring_parameter(notes._padding.__doc__)
    def _pad_direction(self, pad_str):
        """ Pad the data in a specified dimension.

        :param str pad_str: A string of the form 'dim.pad', 'dim.after.pad'\
        or 'dim.before.pad'
        {0}

        """
        pad_vals = pad_str.split('.')
        pplace = None
        pad_place = ['before', 'after']
        if len(pad_vals) == 3:
            pdir, pplace, pval = pad_vals
            remove = list(set(pad_place).difference(set([pplace])))[0]
            pad_place.remove(remove)
        else:
            pdir, pval = pad_vals

        pdir = int(pdir)
        allowed_dims = \
            self.pattern['core_dims'] + (self.pattern['slice_dims'][0],)
        if pdir not in allowed_dims:
            raise Exception('Only core and first slice dimensions, %s, can be '
                            'padded. I cannot pad data dim %s in this plugin.'
                            % (allowed_dims, str(pdir)))
        else:
            for p in pad_place:
                self.padding_dirs[pdir][p] += int(pval)

    def _get_padding_directions(self):
        """ Get padding directions.

        :returns: padding dictionary
        :rtype: dict
        """
        for key in list(self.padding_dirs.keys()):
            if sum(self.padding_dirs[key].values()) == 0:
                del self.padding_dirs[key]
        return self.padding_dirs

    def _get_plugin_padding_directions(self):
        """ Get padding directions.

        :returns: padding dictionary
        :rtype: dict
        """
        for key in list(self.padding_dirs.keys()):
            if sum(self.padding_dirs[key].values()) == 0:
                del self.padding_dirs[key]
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
        if self._is_map:
            ovs = []
            for i in self.get_shape():
                if i != proj_dir[0]:
                    if i != proj_dir[1]:
                        ovs.append(i)
            pattern = \
                {"PROJECTION", {'core_dims': proj_dir, 'slice_dims': ovs}}
        return pattern

    def check_is_tomo(self, proj_dir, rotation):
        pattern = []
        if self._is_tomo:
            ovs = []
            for i in self.get_shape():
                if i != rotation:
                    if i != proj_dir[1]:
                        ovs.append(i)
            pattern = {"SINOGRAM", {'core_dims': (rotation, proj_dir[-1]),
                                    'slice_dims': ovs}}
        return pattern
