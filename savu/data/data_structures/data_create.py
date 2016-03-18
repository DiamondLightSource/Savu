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
.. module:: data_create
   :platform: Unix
   :synopsis: A class inherited by Data class that deals with data object \
   creation.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import copy
import numpy as np


class DataCreate(object):

    def __init__(self, name='DataCreate'):
        self.dtype = None
        self.remove = False

    def create_dataset(self, *args, **kwargs):
        """
        Set up required information when an output dataset has been created by
        a plugin
        """
        self.dtype = kwargs.get('dtype', np.float32)
        # remove from the plugin chain
        self.remove = kwargs.get('remove', False)
        if len(args) is 1:
            self.__copy_dataset(args[0], removeDim=kwargs.get('removeDim', []))
            if args[0].tomo_raw_obj:
                self._set_tomo_raw(copy.deepcopy(args[0].get_tomo_raw()))
                self.get_tomo_raw().data_obj = self
        else:
            try:
                shape = kwargs['shape']
                self.__create_axis_labels(kwargs['axis_labels'])
            except KeyError:
                raise Exception("Please state axis_labels and shape when "
                                "creating a new dataset")
            self.__set_new_dataset_shape(shape)

            if 'patterns' in kwargs:
                self.__copy_patterns(kwargs['patterns'])
        self.get_preview().set_preview([])

    def __set_new_dataset_shape(self, shape):
        if isinstance(shape, DataCreate):
            self.find_and_set_shape(shape)
        elif type(shape) is dict:
            self.set_variable_flag()
            self.set_shape((shape[shape.keys()[0]] + ('var',)))
        else:
            pData = self._get_plugin_data()
            self.set_shape(shape + tuple(pData.extra_dims))
            if 'var' in shape:
                self.set_variable_flag()

    def __copy_patterns(self, copy_data):
        if isinstance(copy_data, DataCreate):
            patterns = copy_data.get_data_patterns()
        else:
            data = copy_data.keys()[0]
            pattern_list = copy_data[data]

            all_patterns = data.get_data_patterns()
            if len(pattern_list[0].split('.')) > 1:
                patterns = self.__copy_patterns_removing_dimensions(
                    pattern_list, all_patterns, len(data.get_shape()))
            else:
                patterns = {}
                for pattern in pattern_list:
                    patterns[pattern] = all_patterns[pattern]
        self.set_data_patterns(patterns)

    def __copy_patterns_removing_dimensions(self, pattern_list, all_patterns,
                                            nDims):
        copy_patterns = {}
        for new_pattern in pattern_list:
            name, all_dims = new_pattern.split('.')
            if name is '*':
                copy_patterns = all_patterns
            else:
                copy_patterns[name] = all_patterns[name]
            dims = tuple(map(int, all_dims.split(',')))
            dims = self._non_negative_directions(dims, nDims=nDims)

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

    def __copy_dataset(self, copy_data, **kwargs):
        if copy_data.mapping:
            # copy label entries from meta data
            map_data = self.exp.index['mapping'][copy_data.get_name()]
            map_mData = map_data.meta_data
            map_axis_labels = map_data.data_info.get_meta_data('axis_labels')
            for axis_label in map_axis_labels:
                if axis_label.keys()[0] in map_mData.get_dictionary().keys():
                    map_label = map_mData.get_meta_data(axis_label.keys()[0])
                    copy_data.meta_data.set_meta_data(axis_label.keys()[0],
                                                      map_label)
            copy_data = map_data
        patterns = copy.deepcopy(copy_data.get_data_patterns())
        self.__copy_labels(copy_data)
        self.find_and_set_shape(copy_data)
        self.set_data_patterns(patterns)

    def __create_axis_labels(self, axis_labels):
        if isinstance(axis_labels, DataCreate):
            self.__copy_labels(axis_labels)
        elif isinstance(axis_labels, dict):
            data = axis_labels.keys()[0]
            self.__copy_labels(data)
            self.__amend_axis_labels(axis_labels[data])
        else:
            self.set_axis_labels(*axis_labels)
            # if parameter tuning
            if self.get_plugin_data().multi_params_dict:
                self.__add_extra_dims_labels()

    def __copy_labels(self, copy_data):
        nDims = copy.copy(copy_data.data_info.get_meta_data('nDims'))
        axis_labels = \
            copy.copy(copy_data.data_info.get_meta_data('axis_labels'))
        self.data_info.set_meta_data('nDims', nDims)
        self.data_info.set_meta_data('axis_labels', axis_labels)
        # if parameter tuning
        if self._get_plugin_data().multi_params_dict:
            self.__add_extra_dims_labels()

    def __add_extra_dims_labels(self):
        params_dict = self.get_plugin_data().multi_params_dict
        # add multi_params axis labels from dictionary in pData
        nDims = self.data_info.get_meta_data('nDims')
        axis_labels = self.data_info.get_meta_data('axis_labels')
        axis_labels.extend([0]*len(params_dict))
        for key, value in params_dict.iteritems():
            title = value['label'].encode('ascii', 'ignore')
            name, unit = title.split('.')
            axis_labels[nDims + key] = {name: unit}
            # add parameter values to the meta_data
            self.meta_data.set_meta_data(name, np.array(value['values']))
        self.data_info.set_meta_data('nDims', nDims + len(self.extra_dims))
        self.data_info.set_meta_data('axis_labels', axis_labels)

    def __amend_axis_labels(self, *args):
        axis_labels = self.data_info.get_meta_data('axis_labels')
        removed_dims = 0
        for arg in args[0]:
            label = arg.split('.')
            if len(label) is 1:
                del axis_labels[int(label[0]) + removed_dims]
                removed_dims += 1
                self.data_info.set_meta_data(
                    'nDims', self.data_info.get_meta_data('nDims') - 1)
            else:
                if int(label[0]) < 0:
                    axis_labels[int(label[0]) + removed_dims] = \
                        {label[1]: label[2]}
                else:
                    if int(label[0]) < self.data_info.get_meta_data('nDims'):
                        axis_labels[int(label[0])] = {label[1]: label[2]}
                    else:
                        axis_labels.insert(int(label[0]), {label[1]: label[2]})

    def set_data_patterns(self, patterns):
        self.add_extra_dims_to_patterns(patterns)
        self.data_info.set_meta_data('data_patterns', patterns)

    def add_extra_dims_to_patterns(self, patterns):
        all_dims = range(len(self.get_shape()))
        for p in patterns:
            pDims = patterns[p]['core_dir'] + patterns[p]['slice_dir']
            for dim in all_dims:
                if dim not in pDims:
                    patterns[p]['slice_dir'] += (dim,)

    def find_and_set_shape(self, data):
        pData = self._get_plugin_data()
        new_shape = copy.copy(data.get_shape()) + tuple(pData.extra_dims)
        self.set_shape(new_shape)
