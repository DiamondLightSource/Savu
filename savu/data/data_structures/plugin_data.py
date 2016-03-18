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
.. module:: plugin_data
   :platform: Unix
   :synopsis: Contains the Data class and all the data structures from which \
   Data can inherit.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from fractions import gcd

from savu.data.meta_data import MetaData


class PluginData(object):

    def __init__(self, data_obj, plugin):
        self.data_obj = data_obj
        self.data_obj._set_plugin_data(self)
        self.meta_data = MetaData()
        self.padding = None
        # this flag determines which data is passed. If false then just the
        # data, if true then all data including dark and flat fields.
        self.selected_data = False
        self.shape = None
        self.core_shape = None
        self.multi_params = {}
        self.extra_dims = []
        self._plugin = plugin

    def get_total_frames(self):
        temp = 1
        slice_dir = \
            self.data_obj.get_data_patterns()[
                self.get_pattern_name()]["slice_dir"]
        for tslice in slice_dir:
            temp *= self.data_obj.get_shape()[tslice]
        return temp

    def set_pattern(self, name):
        pattern = self.data_obj.get_data_patterns()[name]
        self.meta_data.set_meta_data("name", name)
        self.meta_data.set_meta_data("core_dir", pattern['core_dir'])
        self.set_slice_directions()

    def get_pattern_name(self):
        name = self.meta_data.get_meta_data("name")
        if name is not None:
            return name
        else:
            raise Exception("The pattern name has not been set.")

    def get_pattern(self):
        pattern_name = self.get_pattern_name()
        return {pattern_name: self.data_obj.get_data_patterns()[pattern_name]}

    def set_shape(self):
        core_dir = self.get_core_directions()
        slice_dir = self.get_slice_directions()
        dirs = list(set(core_dir + (slice_dir[0],)))
        slice_idx = dirs.index(slice_dir[0])
        shape = []
        for core in set(core_dir):
            shape.append(self.data_obj.get_shape()[core])
        self.set_core_shape(tuple(shape))
        if self.get_frame_chunk() > 1:
            shape.insert(slice_idx, self.get_frame_chunk())
        self.shape = tuple(shape)

    def get_shape(self):
        return self.shape

    def set_core_shape(self, shape):
        self.core_shape = shape

    def get_core_shape(self):
        return self.core_shape

    def check_dimensions(self, indices, core_dir, slice_dir, nDims):
        if len(indices) is not len(slice_dir):
            sys.exit("Incorrect number of indices specified when accessing "
                     "data.")

        if (len(core_dir)+len(slice_dir)) is not nDims:
            sys.exit("Incorrect number of data dimensions specified.")

    def set_slice_directions(self):
        slice_dirs = self.data_obj.get_data_patterns()[
            self.get_pattern_name()]['slice_dir']
        self.meta_data.set_meta_data('slice_dir', slice_dirs)

    def get_slice_directions(self):
        return self.meta_data.get_meta_data('slice_dir')

    def get_slice_dimension(self):
        """
        Return the position of the slice dimension in relation to the data
        handed to the plugin.
        """
        core_dirs = self.get_core_directions()
        slice_dir = self.get_slice_directions()[0]
        return list(set(core_dirs + (slice_dir,))).index(slice_dir)

    def get_data_dimension_by_axis_label(self, label, contains=False):
        """
        Return the dimension of the data in the plugin that has the specified
        axis label.
        """
        label_dim = \
            self.data_obj.find_axis_label_dimension(label, contains=contains)
        plugin_dims = self.get_core_directions()
        if self.get_frame_chunk() > 1:
            plugin_dims += (self.get_slice_directions()[0],)
        return list(set(plugin_dims)).index(label_dim)

    def set_slicing_order(self, order):
        """
        Reorder the slice directions.  The fastest changing slice direction
        will always be the first one. The input param is a tuple stating the
        desired order of slicing directions relative to the current order.
        """
        slice_dirs = self.get_slice_directions()
        if len(slice_dirs) < len(order):
            raise Exception("Incorrect number of dimensions specifed.")
        ordered = [slice_dirs[o] for o in order]
        remaining = [s for s in slice_dirs if s not in ordered]
        new_slice_dirs = tuple(ordered + remaining)
        self.get_current_pattern()['slice_dir'] = new_slice_dirs

    def get_core_directions(self):
        core_dir = self.data_obj.get_data_patterns()[
            self.get_pattern_name()]['core_dir']
        return core_dir

    def set_fixed_directions(self, dims, values):
        slice_dirs = self.get_slice_directions()
        if set(dims).difference(set(slice_dirs)):
            raise Exception("You are trying to fix a direction that is not"
                            " a slicing direction")
        self.meta_data.set_meta_data("fixed_directions", dims)
        self.meta_data.set_meta_data("fixed_directions_values", values)
        self.set_slice_directions()
        shape = list(self.data_obj.get_shape())
        for dim in dims:
            shape[dim] = 1
        self.data_obj.set_shape(tuple(shape))
        self.set_shape()

    def get_fixed_directions(self):
        fixed = []
        values = []
        if 'fixed_directions' in self.meta_data.get_dictionary():
            fixed = self.meta_data.get_meta_data("fixed_directions")
            values = self.meta_data.get_meta_data("fixed_directions_values")
        return [fixed, values]

    def set_frame_chunk(self, nFrames):
        # number of frames to process at a time
        self.meta_data.set_meta_data("nFrames", nFrames)

    def get_frame_chunk(self):
        """ Get the number of frames to be processes at a time.

        If the number of frames is not divisible by the previewing ``chunk``
        value then amend the number of frames to gcd(frames, chunk)

        :returns: Number of frames to process
        :rtype: int
        """
        if self._plugin.chunk:
            frame_chunk = self.meta_data.get_meta_data("nFrames")
            chunk = self.data_obj.get_preview().get_starts_stops_steps(
                key='chunks')[self.get_slice_directions()[0]]
            self.set_frame_chunk(gcd(frame_chunk, chunk))
        return self.meta_data.get_meta_data("nFrames")

    def get_index(self, indices):
        shape = self.get_shape()
        nDims = len(shape)
        name = self.get_current_pattern_name()
        ddirs = self.get_data_patterns()
        core_dir = ddirs[name]["core_dir"]
        slice_dir = ddirs[name]["slice_dir"]

        self.check_dimensions(indices, core_dir, slice_dir, nDims)

        index = [slice(None)]*nDims
        count = 0
        for tdir in slice_dir:
            index[tdir] = slice(indices[count], indices[count]+1, 1)
            count += 1

        return tuple(index)

    def plugin_data_setup(self, pattern_name, chunk):
        self.set_pattern(pattern_name)
        chunks = \
            self.data_obj.get_preview().get_starts_stops_steps(key='chunks')
        if (chunks[self.get_slice_directions()[0]] % chunk):
            self._plugin.chunk = True
        self.set_frame_chunk(chunk)
        self.set_shape()

    def set_temp_pad_dict(self, pad_dict):
        self.meta_data.set_meta_data('temp_pad_dict', pad_dict)

    def get_temp_pad_dict(self):
        if 'temp_pad_dict' in self.meta_data.get_dictionary().keys():
            return self.meta_data.get_dictionary()['temp_pad_dict']

    def delete_temp_pad_dict(self):
        del self.meta_data.get_dictionary()['temp_pad_dict']
