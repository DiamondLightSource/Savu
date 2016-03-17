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
.. module:: data
   :platform: Unix
   :synopsis: The Data class dynamically inherits from transport specific data\
   class and holds the data array, along with associated information.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import copy

import numpy as np

import savu.data.data_structures.utils as dsu
import savu.core.utils as cu
from savu.data.meta_data import MetaData
from savu.data.data_structures.data_create import DataCreate
from savu.core.utils import docstring_parameter


class Data(DataCreate):
    """The Data class dynamically inherits from transport specific data class
    and holds the data array, along with associated information.
    """

    def __init__(self, name, exp):
        super(Data, self).__init__(name)
        self.meta_data = MetaData()
        self.pattern_list = self.set_available_pattern_list()
        self.data_info = MetaData()
        self.__initialise_data_info(name)
        self.exp = exp
        self.group_name = None
        self.group = None
        self._plugin_data_obj = None
        self.tomo_raw_obj = None
        self.data_mapping = None
        self.backing_file = None
        self.data = None
        self.next_shape = None
        self.mapping = None
        self.map_dim = []
        self.revert_shape = None

    def __initialise_data_info(self, name):
        """ Initialise entries in the data_info meta data.
        """
        self.data_info.set_meta_data('name', name)
        self.data_info.set_meta_data('data_patterns', {})
        self.data_info.set_meta_data('shape', None)
        self.data_info.set_meta_data('nDims', None)

    def _set_plugin_data(self, plugin_data_obj):
        """ Encapsulate a PluginData object.
        """
        self._plugin_data_obj = plugin_data_obj

    def _clear_plugin_data(self):
        """ Set encapsulated PluginData object to None.
        """
        self._plugin_data_obj = None

    def _get_plugin_data(self):
        """ Get encapsulated PluginData object.
        """
        if self._plugin_data_obj is not None:
            return self._plugin_data_obj
        else:
            raise Exception("There is no PluginData object associated with "
                            "the Data object.")

    def _set_tomo_raw(self, tomo_raw_obj):
        """ Encapsulate a TomoRaw object.
        """
        self.tomo_raw_obj = tomo_raw_obj

    def _clear_tomo_raw(self):
        """ Set encapsulated TomoRaw object to None.
        """
        self.tomo_raw_obj = None

    def get_tomo_raw(self):
        """ Get encapsulated TomoRaw object.

        :return: associated TomoRaw object if available.
        :rtype: TomoRaw
        """
        if self.tomo_raw_obj is not None:
            return self.tomo_raw_obj
        else:
            raise Exception("There is no TomoRaw object associated with "
                            "the Data object.")

    def _get_transport_data(self):
        """ Import the data transport mechanism

        :returns: instance of data transport
        :rtype: transport_data
        """
        transport = self.exp.meta_data.get_meta_data("transport")
        transport_data = "savu.data.transport_data." + transport + \
                         "_transport_data"
        return cu.import_class(transport_data)

    def __deepcopy__(self, memo):
        """ Copy the data object.
        """
        name = self.data_info.get_meta_data('name')
        return dsu._deepcopy_data_object(self, Data(name, self.exp))

    def get_data_patterns(self):
        """ Get data patterns associated with this data object.

        :returns: A dictionary of associated patterns.
        :rtype: dict
        """
        return self.data_info.get_meta_data('data_patterns')

    def set_shape(self, shape):
        """ Set the dataset shape.
        """
        self.data_info.set_meta_data('shape', shape)
        self.check_dims()

    def get_shape(self):
        """ Get the dataset shape

        :returns: data shape
        :rtype: tuple
        """
        shape = self.data_info.get_meta_data('shape')
        return shape

    @docstring_parameter(dsu.set_preview_note.__doc__)
    def set_preview(self, preview_list, **kwargs):
        """ Reduces the data to be processed to a subset of the original.

        :param list preview: previewing parameters, where
            ``len(preview_list)`` equals the number of data dimensions.
        :keyword bool revert: revert input dataset to the original size after
         plugin processing.

        {0}
        """

        self.revert_shape = kwargs.get('revert', self.revert_shape)
        shape = self.get_shape()
        if preview_list:
            preview_list = self.add_preview_defaults(preview_list)
            starts, stops, steps, chunks = \
                self.get_preview_indices(preview_list)
            shape_change = True
        else:
            starts, stops, steps, chunks = \
                [[0]*len(shape), shape, [1]*len(shape), [1]*len(shape)]
            shape_change = False
        self.set_starts_stops_steps(starts, stops, steps, chunks,
                                    shapeChange=shape_change)

    def add_preview_defaults(self, plist):
        nEntries = 4
        diff_len = [(nEntries - len(elem.split(':'))) for elem in plist]
        all_idx = [i for i in range(len(plist)) if plist[i] == ':']
        amend = [i for i in range(len(plist)) if diff_len and i not in all_idx]
        for idx in amend:
            plist[idx] += ':1'*diff_len[idx]
        return plist

    def unset_preview(self):
        self.set_preview([])
        self.set_shape(self.revert_shape)
        self.revert_shape = None

    def set_starts_stops_steps(self, starts, stops, steps, chunks,
                               shapeChange=True):
        self.data_info.set_meta_data('starts', starts)
        self.data_info.set_meta_data('stops', stops)
        self.data_info.set_meta_data('steps', steps)
        self.data_info.set_meta_data('chunks', chunks)
        if shapeChange or self.mapping:
            self.set_reduced_shape(starts, stops, steps, chunks)

    def get_preview_indices(self, preview_list):
        starts = len(preview_list)*[None]
        stops = len(preview_list)*[None]
        steps = len(preview_list)*[None]
        chunks = len(preview_list)*[None]

        for i in range(len(preview_list)):
            if preview_list[i] is ':':
                preview_list[i] = '0:end:1:1'
            starts[i], stops[i], steps[i], chunks[i] = \
                self.convert_indices(preview_list[i].split(':'), i)
        return starts, stops, steps, chunks

    def convert_indices(self, idx, dim):
        shape = self.get_shape()
        mid = shape[dim]/2
        end = shape[dim]

        if self.mapping:
            map_shape = self.exp.index['mapping'][self.get_name()].get_shape()
            midmap = map_shape[dim]/2
            endmap = map_shape[dim]

        idx = [eval(equ) for equ in idx]
        idx = [idx[i] if idx[i] > -1 else shape[dim]+1+idx[i] for i in
               range(len(idx))]
        return idx

    def get_starts_stops_steps(self):
        starts = self.data_info.get_meta_data('starts')
        stops = self.data_info.get_meta_data('stops')
        steps = self.data_info.get_meta_data('steps')
        chunks = self.data_info.get_meta_data('chunks')
        return starts, stops, steps, chunks

    def set_reduced_shape(self, starts, stops, steps, chunks):
        orig_shape = self.get_shape()
        self.data_info.set_meta_data('orig_shape', orig_shape)
        new_shape = []
        for dim in range(len(starts)):
            new_shape.append(np.prod((self.get_slice_dir_matrix(dim).shape)))
        self.set_shape(tuple(new_shape))

        # reduce shape of mapping data if it exists
        if self.mapping:
            self.set_mapping_reduced_shape(orig_shape, new_shape,
                                           self.get_name())

    def set_mapping_reduced_shape(self, orig_shape, new_shape, name):
        map_obj = self.exp.index['mapping'][name]
        map_shape = np.array(map_obj.get_shape())
        diff = np.array(orig_shape) - map_shape[:len(orig_shape)]
        not_map_dim = np.where(diff == 0)[0]
        map_dim = np.where(diff != 0)[0]
        self.map_dim = map_dim
        map_obj.data_info.set_meta_data('full_map_dim_len', map_shape[map_dim])
        map_shape[not_map_dim] = np.array(new_shape)[not_map_dim]

        # assuming only one extra dimension added for now
        starts, stops, steps, chunks = self.get_starts_stops_steps()
        start = starts[map_dim] % map_shape[map_dim]
        stop = min(stops[map_dim], map_shape[map_dim])

        temp = len(np.arange(start, stop, steps[map_dim]))*chunks[map_dim]
        map_shape[len(orig_shape)] = np.ceil(new_shape[map_dim]/temp)
        map_shape[map_dim] = new_shape[map_dim]/map_shape[len(orig_shape)]
        map_obj.data_info.set_meta_data('map_dim_len', map_shape[map_dim])
        self.exp.index['mapping'][name].set_shape(tuple(map_shape))

    def find_and_set_shape(self, data):
        pData = self._get_plugin_data()
        new_shape = copy.copy(data.get_shape()) + tuple(pData.extra_dims)
        self.set_shape(new_shape)

    def check_dims(self):
        nDims = self.data_info.get_meta_data("nDims")
        shape = self.data_info.get_meta_data('shape')
        if nDims:
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
                        "VOLUME_3D",
                        "SPECTRUM",
                        "DIFFRACTION",
                        "CHANNEL",
                        "SPECTRUM_STACK",
                        "PROJECTION_STACK",
                        "METADATA"]
        return pattern_list

    def add_pattern(self, dtype, **kwargs):
        if dtype in self.pattern_list:
            nDims = 0
            for args in kwargs:
                nDims += len(kwargs[args])
                self.data_info.set_meta_data(['data_patterns', dtype, args],
                                             kwargs[args])
            self.convert_pattern_directions(dtype)
            if self.get_shape():
                diff = len(self.get_shape()) - nDims
                if diff:
                    pattern = {dtype: self.get_data_patterns()[dtype]}
                    self.add_extra_dims_to_patterns(pattern)
                    nDims += diff
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
        self.add_pattern("VOLUME_YZ", **self.get_dirs_for_volume(y, z, x))
        self.add_pattern("VOLUME_XZ", **self.get_dirs_for_volume(x, z, y))
        self.add_pattern("VOLUME_XY", **self.get_dirs_for_volume(x, y, z))

    def get_dirs_for_volume(self, dim1, dim2, sdir):
        all_dims = range(len(self.get_shape()))
        vol_dict = {}
        vol_dict['core_dir'] = (dim1, dim2)
        slice_dir = [sdir]
        # *** need to add this for other patterns
        for ddir in all_dims:
            if ddir not in [dim1, dim2, sdir]:
                slice_dir.append(ddir)
        vol_dict['slice_dir'] = tuple(slice_dir)
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

    def find_axis_label_dimension(self, name, contains=False):
        axis_labels = self.data_info.get_meta_data('axis_labels')
        for i in range(len(axis_labels)):
            if contains is True:
                for names in axis_labels[i].keys():
                    if name in names:
                        return i
            else:
                if name in axis_labels[i].keys():
                    return i
        raise Exception("Cannot find the specifed axis label.")

    def finalise_patterns(self):
        check = 0
        check += self.check_pattern('SINOGRAM')
        check += self.check_pattern('PROJECTION')
        if check is 2:
            self.set_main_axis('SINOGRAM')
            self.set_main_axis('PROJECTION')
        elif check is 1:
            pass

    def check_pattern(self, pattern_name):
        patterns = self.get_data_patterns()
        try:
            patterns[pattern_name]
        except KeyError:
            return 0
        return 1

    def convert_pattern_directions(self, dtype):
        pattern = self.get_data_patterns()[dtype]
        nDims = sum([len(i) for i in pattern.values()])
        for p in pattern:
            ddirs = pattern[p]
            pattern[p] = self.non_negative_directions(ddirs, nDims)

    def non_negative_directions(self, ddirs, nDims):
        index = [i for i in range(len(ddirs)) if ddirs[i] < 0]
        list_ddirs = list(ddirs)
        for i in index:
            list_ddirs[i] = nDims + ddirs[i]
        return tuple(list_ddirs)

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
            self.set_preview([])

    def get_axis_label_keys(self):
        axis_labels = self.data_info.get_meta_data('axis_labels')
        axis_label_keys = []
        for labels in axis_labels:
            for key in labels.keys():
                axis_label_keys.append(key)
        return axis_label_keys

    def get_current_and_next_patterns(self, datasets_lists):
        current_datasets = datasets_lists[0]
        patterns_list = []
        for current_data in current_datasets['out_datasets']:
            current_name = current_data['name']
            current_pattern = current_data['pattern']
            next_pattern = self.find_next_pattern(datasets_lists[1:],
                                                  current_name)
            patterns_list.append({'current': current_pattern,
                                  'next': next_pattern})
        self.exp.meta_data.set_meta_data('current_and_next', patterns_list)

    def find_next_pattern(self, datasets_lists, current_name):
        next_pattern = []
        for next_data_list in datasets_lists:
            for next_data in next_data_list['in_datasets']:
                if next_data['name'] == current_name:
                    next_pattern = next_data['pattern']
                    return next_pattern
        return next_pattern

#    def find_next_pattern(self, datasets_lists, current_name):
#        next_pattern = []
#        print "next_data_list", next_data_list
#        for next_data_list in datasets_lists:
#            for next_data in next_data_list['in_datasets']:
#                if next_data['name'] == current_name:
#                    next_pattern = next_data['pattern']
#                    return next_pattern
#        return next_pattern
