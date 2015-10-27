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
.. module:: data_structures
   :platform: Unix
   :synopsis: Contains the Data class and all the data structures from which
   Data can inherit.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import sys
import logging
import warnings
import copy

import h5py
import numpy as np

from savu.data.meta_data import MetaData


class Data(object):
    """
    The Data class dynamically inherits from relevant data structure classes
    at runtime and holds the data array.
    """

    def __init__(self, name, exp):
        self.meta_data = MetaData()
        self.pattern_list = self.set_available_pattern_list()
        self.data_info = MetaData()
        self.initialise_data_info(name)
        self.exp = exp
        self.group_name = None
        self.group = None
        self.backing_file = None
        self.data = None
        self._plugin_data_obj = None
        self.tomo_raw_obj = None
        self.data_mapping = None
        self.variable_length_flag = False
        self.dtype = None
        self.remove = False

    def initialise_data_info(self, name):
        self.data_info.set_meta_data('name', name)
        self.data_info.set_meta_data('data_patterns', {})
        self.data_info.set_meta_data('shape', None)
        self.data_info.set_meta_data('nDims', None)

    def set_plugin_data(self, plugin_data_obj):
        self._plugin_data_obj = plugin_data_obj

    def clear_plugin_data(self):
        self._plugin_data_obj = None

    def get_plugin_data(self):
        if self._plugin_data_obj is not None:
            return self._plugin_data_obj
        else:
            raise Exception("There is no PluginData object associated with "
                            "the Data object.")

    def set_tomo_raw(self, tomo_raw_obj):
        self.tomo_raw_obj = tomo_raw_obj

    def clear_tomo_raw(self):
        self.tomo_raw_obj = None

    def get_tomo_raw(self):
        if self.tomo_raw_obj is not None:
            return self.tomo_raw_obj
        else:
            raise Exception("There is no TomoRaw object associated with "
                            "the Data object.")

    def get_transport_data(self, transport):
        transport_data = "savu.data.transport_data." + transport + \
                         "_transport_data"
        return self.import_class(transport_data)

    def import_class(self, class_name):
        name = class_name
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        temp = name.split('.')[-1]
        module2class = ''.join(x.capitalize() for x in temp.split('_'))
        return getattr(mod, module2class.split('.')[-1])

    def __deepcopy__(self, memo):
        return self

#    def __deepcopy__(self, memo):
#        newobj = TomoRaw(self.data_obj)
#        newobj.image_key = self.image_key
#        newobj.image_key_slice = copy.deepcopy(self.image_key_slice)
#        newobj.frame_list = copy.deepcopy(self.frame_list)
#        newobj.data_only_flag = copy.deepcopy(self.data_only_flag)
#        return newobj

    def add_base(self, ExtraBase):
        cls = self.__class__
        self.__class__ = cls.__class__(cls.__name__, (cls, ExtraBase), {})
        ExtraBase().__init__()

    def add_base_classes(self, bases):
        for base in bases:
            self.add_base(base)

    def external_link(self):
        return h5py.ExternalLink(self.backing_file.filename, self.group_name)

    def create_dataset(self, *args, **kwargs):
        """
        Set up required information when an output dataset has been created by
        a plugin
        """
        self.dtype = kwargs.get('dtype', np.float32)
        # remove from the plugin chain
        self.remove = kwargs.get('remove', False)
        if len(args) is 1:
            self.copy_dataset(args[0], removeDim=kwargs.get('removeDim', []))
            if args[0].tomo_raw_obj:
                self.set_tomo_raw(copy.deepcopy(args[0].get_tomo_raw()))
                self.get_tomo_raw().data_obj = self
            if args[0].get_variable_flag():
                self.set_variable_flag()
        else:
            try:
                self.create_axis_labels(kwargs['axis_labels'])
                shape = kwargs['shape']
                if isinstance(shape, Data):
                    self.set_shape(Data.get_shape())
                elif type(shape) is dict:
                    self.set_variable_flag()
                    self.set_shape((shape[shape.keys()[0]] + ('var',)))
                else:
                    self.set_shape(shape)
                    if 'var' in shape:
                        self.set_variable_flag()
            except KeyError:
                raise Exception("Please state axis_labels and shape when "
                                "creating a new dataset")
            try:
                self.copy_patterns(kwargs['patterns'])
            except KeyError:
                pass

    def copy_patterns(self, copy_data):
        if isinstance(copy_data, Data):
            patterns = copy_data.get_data_patterns()
        else:
            data = copy_data.keys()[0]
            pattern_list = copy_data[data]

            all_patterns = data.get_data_patterns()
            if len(pattern_list[0].split('.')) > 1:
                patterns = self.copy_patterns_removing_dimensions(
                    pattern_list, all_patterns, len(data.get_shape()))
            else:
                patterns = {}
                for pattern in pattern_list:
                    patterns[pattern] = all_patterns[pattern]

        self.set_data_patterns(patterns)

    def copy_patterns_removing_dimensions(self, pattern_list, all_patterns,
                                          nDims):
        copy_patterns = {}
        for new_pattern in pattern_list:
            name, all_dims = new_pattern.split('.')
            if name is '*':
                copy_patterns = all_patterns
            else:
                copy_patterns[name] = all_patterns[name]
            dims = tuple(map(int, all_dims.split(',')))
            dims = self.non_negative_directions(dims, nDims=nDims)

        patterns = {}
        for name, pattern_dict in copy_patterns.iteritems():
            empty_flag = False
            for ddir in pattern_dict:
                s_dims = self.non_negative_directions(
                    pattern_dict[ddir], nDims=nDims)
                new_dims = tuple([sd for sd in s_dims if sd not in dims])
                pattern_dict[ddir] = new_dims
                if not new_dims:
                    empty_flag = True
            if empty_flag is False:
                patterns[name] = pattern_dict
        return patterns

    def copy_dataset(self, copy_data, **kwargs):
        patterns = copy.copy(copy_data.get_data_patterns())
        self.set_data_patterns(patterns)
        self.copy_labels(copy_data)
        shape = copy_data.get_shape()
        self.set_shape(shape)

    def create_axis_labels(self, axis_labels):
        if isinstance(axis_labels, Data):
            self.copy_labels(axis_labels)
        elif isinstance(axis_labels, dict):
            data = axis_labels.keys()[0]
            self.copy_labels(data)
            self.amend_axis_labels(axis_labels[data])
        else:
            self.set_axis_labels(*axis_labels)

    def copy_labels(self, copy_data):
        nDims = copy.copy(copy_data.data_info.get_meta_data('nDims'))
        self.data_info.set_meta_data('nDims', nDims)
        axis_labels = copy.copy(
            copy_data.data_info.get_meta_data('axis_labels'))
        self.data_info.set_meta_data('axis_labels', axis_labels)

    def amend_axis_labels(self, *args):
        axis_labels = self.data_info.get_meta_data('axis_labels')
        removed_dims = 0
        for arg in args[0]:
            label = arg.split('.')
            if len(label) is 1:
                print "deleting", int(label[0]) + removed_dims
                del axis_labels[int(label[0]) + removed_dims]
                removed_dims += 1
                self.data_info.set_meta_data(
                    'nDims', self.data_info.get_meta_data('nDims') - 1)
            else:
                if int(label[0]) < 0:
                    axis_labels[int(label[0]) + removed_dims] = \
                        {label[1]: label[2]}
                else:
                    axis_labels.insert(int(label[0]), {label[1]: label[2]})

    def set_data_patterns(self, patterns):
        self.data_info.set_meta_data('data_patterns', patterns)

    def get_data_patterns(self):
        return self.data_info.get_meta_data('data_patterns')

    def set_shape(self, shape):
        self.data_info.set_meta_data('shape', shape)
        self.check_dims()

    def get_shape(self):
        shape = self.data_info.get_meta_data('shape')
        try:
            dirs = self.meta_data.get_meta_data("fixed_directions")
            shape = list(self.shape)
            for ddir in dirs:
                shape[ddir] = 1
            shape = tuple(shape)
        except KeyError:
            pass
        return shape

    def set_variable_flag(self):
        self.variable_length_flag = True

    def get_variable_flag(self):
        return self.variable_length_flag

    def remove_variable_length(self, length):
        self.variable_length_flag = False
        shape = list(self.get_shape())
        index = [i for i in range(len(shape)) if i is 'var']
        shape[index] = length
        print "the index", index, shape
        self.set_shape(tuple(shape))

    def check_dims(self):
        nDims = self.data_info.get_meta_data("nDims")
        shape = self.data_info.get_meta_data('shape')
        if nDims:
            if self.get_variable_flag() is False:
                if len(shape) != nDims:
                    error_msg = ("The number of axis labels, %d, does not "
                                 "coincide with the number of data "
                                 "dimensions %d." % (nDims, len(shape)))
                    raise Exception(error_msg)

    def set_name(self, name):
        self.data_info.set_meta_data('name', name)

    def get_name(self):
        return self.data_info.get_meta_data('name')

    def set_data_params(self, pattern, chunk_size, **kwargs):
        self.set_current_pattern_name(pattern)
        self.set_nFrames(chunk_size)

    def set_available_pattern_list(self):
        pattern_list = ["SINOGRAM",
                        "PROJECTION",
                        "VOLUME_YZ",
                        "VOLUME_XZ",
                        "VOLUME_XY",
                        "SPECTRUM",
                        "DIFFRACTION",
                        "CHANNEL",
                        "SPECTRUM_STACK",
                        "1D_METADATA"]
                        # added spectrum adp 17th August,
                        # Added diffraction 28th August adp
        return pattern_list

    def add_pattern(self, dtype, **kwargs):
        if dtype in self.pattern_list:
            nDims = 0
            for args in kwargs:
                nDims += len(kwargs[args])
                self.data_info.set_meta_data(['data_patterns', dtype, args],
                                             kwargs[args])
            try:
                if nDims != self.data_info.get_meta_data("nDims"):
                    actualDims = self.data_info.get_meta_data('nDims')
                    err_msg = ("The pattern %s has an incorrect number of "
                               "dimensions: %d required but %d specified."
                               % (dtype, actualDims, nDims))
                    raise Exception(err_msg)
            except KeyError:
                self.data_info.set_meta_data('nDims', nDims)
        else:
            raise Exception("The data pattern '%s'does not exist. Please "
                            "choose from the following list: \n'%s'",
                            dtype, str(self.pattern_list))

    def add_volume_patterns(self, x, y, z):
        self.add_pattern("VOLUME_YZ", **self.get_dirs_for_volume(y, z))
        self.add_pattern("VOLUME_XZ", **self.get_dirs_for_volume(x, z))
        self.add_pattern("VOLUME_XY", **self.get_dirs_for_volume(x, y))

    def get_dirs_for_volume(self, dim1, dim2):
        all_dims = range(len(self.get_shape()))
        vol_dict = {}
        vol_dict['core_dir'] = (dim1, dim2)
        slice_dir = tuple([a for a in all_dims if a not in [dim1, dim2]])
        vol_dict['slice_dir'] = slice_dir
        return vol_dict

    def set_axis_labels(self, *args):
        self.data_info.set_meta_data('nDims', len(args))
        axis_labels = []
        for arg in args:
            try:
                axis = arg.split('.')
                axis_labels.append({axis[0]: axis[1]})
            except:
                # data arrives here, but that may be an error
                pass
        self.data_info.set_meta_data('axis_labels', axis_labels)

    def finalise_patterns(self):
        check = 0
        check += self.check_pattern('SINOGRAM')
        check += self.check_pattern('PROJECTION')
        if check is 2:
            self.set_main_axis('SINOGRAM')
            self.set_main_axis('PROJECTION')
        elif check is 1:
            raise Exception("Cannot set up SINOGRAM and PROJECTION "
                            "main_directions as both patterns do not exist")

    def check_pattern(self, pattern_name):
        patterns = self.get_data_patterns()
        try:
            patterns[pattern_name]
        except KeyError:
            return 0
        return 1

    def non_negative_directions(self, ddirs, **kwargs):
        try:
            nDims = kwargs['nDims']
        except KeyError:
            nDims = len(self.get_shape())
        print "ddirs", ddirs
        index = [i for i in range(len(ddirs)) if ddirs[i] < 0]
        list_ddirs = list(ddirs)
        for i in index:
            list_ddirs[i] = nDims + ddirs[i]
        index = tuple(list_ddirs)
        return index

#    def set_direction_parallel_to_rotation_axis(self, tdir):
#        self.check_direction(tdir, 'parallel_to_rotation_axis')
#        self.set_main_axis(tdir, 'SINOGRAM')
#
#    def set_direction_perp_to_rotation_axis(self, tdir):
#        self.check_direction(tdir, 'perp_to_rotation_axis')
#        self.set_main_axis(tdir, 'PROJECTION')

    def check_direction(self, tdir, dname):
        if not isinstance(tdir, int):
            raise TypeError('The direction should be an integer.')

        patterns = self.get_data_patterns()
        if not patterns:
            raise Exception("Please add available patterns before setting the"
                            " direction ", dname)

    def set_main_axis(self, pname):
        patterns = self.get_data_patterns()
        n1 = 'PROJECTION' if pname is 'SINOGRAM' else 'SINOGRAM'
        d1 = patterns[n1]['core_dir']
        d2 = patterns[pname]['slice_dir']
        tdir = set(d1).intersection(set(d2))
        self.data_info.set_meta_data(['data_patterns', pname, 'main_dir'],
                                     list(tdir)[0])

    def trim_input_data(self, **kwargs):
        if self.tomo_raw_obj:
            self.get_tomo_raw().select_image_key(**kwargs)

    def trim_output_data(self, copy_obj, **kwargs):
        if self.tomo_raw_obj:
            self.get_tomo_raw().remove_image_key(copy_obj, **kwargs)

    def get_axis_label_keys(self):
        axis_labels = self.data_info.get_meta_data('axis_labels')
        axis_label_keys = []
        for labels in axis_labels:
            for key in labels.keys():
                axis_label_keys.append(key)
        return axis_label_keys


class PluginData(object):

    def __init__(self, data_obj):
        self.data_obj = data_obj
        self.data_obj.set_plugin_data(self)
        self.meta_data = MetaData()
        self.padding = None
        # this flag determines which data is passed. If false then just the
        # data, if true then all data including dark and flat fields.
        self.selected_data = False

    def get_total_frames(self):
        temp = 1
        slice_dir = \
            self.data_obj.get_data_patterns()[
                self.get_pattern_name()]["slice_dir"]
        for tslice in slice_dir:
            temp *= self.data_obj.get_shape()[tslice]
        return temp

    def set_pattern_name(self, name):
        self.meta_data.set_meta_data("name", name)
        self.check_data_type_exists()

    def get_pattern_name(self):
        name = self.meta_data.get_meta_data("name")
        if name is not None:
            return name
        else:
            raise Exception("The pattern name has not been set.")

    def get_pattern(self):
        pattern_name = self.get_pattern_name()
        return {pattern_name: self.data_obj.get_data_patterns()[pattern_name]}

    def get_shape(self):
        return self.get_sub_shape(self.get_pattern_name())

    def check_dimensions(self, indices, core_dir, slice_dir, nDims):
        if len(indices) is not len(slice_dir):
            sys.exit("Incorrect number of indices specified when accessing "
                     "data.")

        if (len(core_dir)+len(slice_dir)) is not nDims:
            sys.exit("Incorrect number of data dimensions specified.")

    def check_data_type_exists(self):
        if self.get_pattern_name() not in \
                self.data_obj.pattern_list:
            raise Exception(("Error: The Data class does not contain an \
                              instance of ", self.get_pattern_name()))

    def get_slice_directions(self):
        try:
            [fix_dirs, value] = self.get_fixed_directions()
        except KeyError:
            fix_dirs = []
        slice_dirs = self.data_obj.get_data_patterns()[
            self.get_pattern_name()]['slice_dir']
        to_slice = [sd for sd in slice_dirs if sd not in fix_dirs]
        temp = self.data_obj.non_negative_directions(tuple(to_slice))
        return temp

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
        return self.data_obj.non_negative_directions(core_dir)

    def set_fixed_directions(self, dims, values):
        slice_dirs = self.get_slice_directions()
        for dim in dims:
            if dim in slice_dirs:
                self.meta_data.set_meta_data("fixed_directions", dims)
                self.meta_data.set_meta_data("fixed_directions_values", values)
            else:
                raise Exception("You are trying to fix a direction that is not"
                                " a slicing direction")

    def get_fixed_directions(self):
        try:
            fixed = self.meta_data.get_meta_data("fixed_directions")
            values = self.meta_data.\
                get_meta_data("fixed_directions_values")
        except KeyError:
            fixed = []
            values = []
        return [fixed, values]

    def delete_fixed_directions(self):
        try:
            del self.meta_data.dict["fixed_directions"]
            del self.meta_data.dict["fixed_directions_values"]
        except KeyError:
            pass

    def set_frame_chunk(self, nFrames):
        # number of frames to process at a time
        self.meta_data.set_meta_data("nFrames", nFrames)

    def get_frame_chunk(self):
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

    def get_sub_shape(self, name):
        core_dir = self.get_core_directions()
        shape = []
        for core in core_dir:
            shape.append(self.data_obj.get_shape()[core])
        return tuple(shape)

    def plugin_data_setup(self, pattern_name, chunk):
        try:
            self.set_pattern_name(pattern_name)
            self.set_frame_chunk(chunk)
        except KeyError:
            raise Exception("When calling plugin_data_setup(), pattern_name "
                            "and chunk are required as kwargs.")


class TomoRaw(object):

    def __init__(self, data_obj):
        self.data_obj = data_obj
        self.data_obj.set_tomo_raw(self)
        self.image_key_slice = None
        self.frame_list = []

    def select_image_key(self, **kwargs):
        image_key = kwargs['image_key']
        self.data_obj.get_plugin_data().selected_data = True
        self.set_image_key_slice(image_key)

    def remove_image_key(self, copy_obj, **kwargs):
        image_key = kwargs.get('image_key', 0)
        if image_key is 0:
            if copy_obj.tomo_raw_obj:
                self.data_obj.set_shape(
                    copy_obj.get_tomo_raw().remove_dark_and_flat())
                self.data_obj.clear_tomo_raw()

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
        pattern = self.data_obj.get_plugin_data().get_pattern_name()
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
        
