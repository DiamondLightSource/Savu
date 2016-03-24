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

import savu.data.data_structures.data_notes as notes
from savu.core.utils import docstring_parameter


class DataCreate(object):
    """ Class that deals with creating a data object.
    """

    def __init__(self, name='DataCreate'):
        self.dtype = None
        self.remove = False

    @docstring_parameter(notes._create.__doc__, notes._shape.__doc__,
                         notes.axis_labels.__doc__, notes.patterns.__doc__)
    def create_dataset(self, *args, **kwargs):
        """ Set up required information when an output dataset has been
        created by a plugin.

        :arg Data: A data object
        :keyword tuple shape: The shape of the dataset
        :keyword list axis_labels: The axis_labels associated with the datasets
        :keyword patterns: The patterns associated with the dataset (optional,
            see note below)
        :keyword type dtype: Type of the data (optional: Defaults to
            np.float32)
        :keyword bool remove: Remove from framework after completion
        (no link in .nxs file) (optional: Defaults to False.)

        {0} \n {1} \n {2} \n {3}

        """
        self.dtype = kwargs.get('dtype', np.float32)
        self.remove = kwargs.get('remove', False)
        if len(args) is 1:
            self.__create_dataset_from_object(args[0])
        else:
            self.__create_dataset_from_kwargs(kwargs)
        self.get_preview().set_preview([])

    def __create_dataset_from_object(self, data_obj):
        """ Create a dataset from an existing Data object.
        """
        if data_obj.mapping:
            data_obj = self.__copy_mapping_object(data_obj)
        patterns = copy.deepcopy(data_obj.get_data_patterns())
        self.__copy_labels(data_obj)
        self.__find_and_set_shape(data_obj)
        self.__set_data_patterns(patterns)
        if data_obj.tomo_raw_obj:
            self._set_tomo_raw(copy.deepcopy(data_obj.get_tomo_raw()))
            self.get_tomo_raw().data_obj = self

    def __copy_mapping_object(self, data_obj):
        """ Copy relevant mapping object information and return the mapping
        Data object
        """
        map_data = self.exp.index['mapping'][data_obj.get_name()]
        map_mData = map_data.meta_data
        map_axis_labels = map_data.data_info.get_meta_data('axis_labels')
        for axis_label in map_axis_labels:
            if axis_label.keys()[0] in map_mData.get_dictionary().keys():
                map_label = map_mData.get_meta_data(axis_label.keys()[0])
                data_obj.meta_data.set_meta_data(axis_label.keys()[0],
                                                 map_label)
        return map_data

    def __create_dataset_from_kwargs(self, kwargs):
        """ Create dataset from kwargs. """
        try:
            shape = kwargs['shape']
            self.__create_axis_labels(kwargs['axis_labels'])
        except KeyError:
            raise Exception("Please state axis_labels and shape when "
                            "creating a new dataset")

        if isinstance(shape, DataCreate):
            self.__find_and_set_shape(shape)
        else:
            pData = self._get_plugin_data()
            self.set_shape(shape + tuple(pData.extra_dims))
        if 'patterns' in kwargs:
            patterns = self.__copy_patterns(kwargs['patterns'])
            self.__set_data_patterns(patterns)

    def __copy_patterns(self, copy_data):
        """ Copy patterns """
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
        return patterns

    def __copy_patterns_removing_dimensions(self, pattern_list, all_patterns,
                                            nDims):
        """ Copy patterns but remove specified dimensions from them. """
        copy_patterns = {}
        for new_pattern in pattern_list:
            name, all_dims = new_pattern.split('.')
            if name is '*':
                copy_patterns = all_patterns
            else:
                copy_patterns[name] = all_patterns[name]
            dims = tuple(map(int, all_dims.split(',')))
            dims = self.non_negative_directions(dims, nDims=nDims)

        dim_map = [a for a in range(nDims) if a not in dims]
        patterns = {}
        for name, pattern_dict in copy_patterns.iteritems():
            empty_flag = False
            for ddir in pattern_dict:
                s_dims = self.non_negative_directions(
                    pattern_dict[ddir], nDims=nDims)
                new_dims = [sd for sd in s_dims if sd not in dims]
                new_dims = [dim_map.index(n) for n in new_dims]
                pattern_dict[ddir] = tuple(new_dims)
                if not new_dims:
                    empty_flag = True
            if empty_flag is False:
                patterns[name] = pattern_dict
        return patterns

    def __create_axis_labels(self, axis_labels):
        """ Create axis labels. """
        if isinstance(axis_labels, DataCreate):
            self.__copy_labels(axis_labels)
        elif isinstance(axis_labels, dict):
            data = axis_labels.keys()[0]
            self.__copy_labels(data)
            self.__amend_axis_labels(axis_labels[data])
        else:
            self.set_axis_labels(*axis_labels)
            # if parameter tuning
            if self._get_plugin_data().multi_params_dict:
                self.__add_extra_dims_labels()

    def __copy_labels(self, copy_data):
        """ Copy axis labels. """
        nDims = copy.copy(copy_data.data_info.get_meta_data('nDims'))
        axis_labels = \
            copy.copy(copy_data.data_info.get_meta_data('axis_labels'))
        self.data_info.set_meta_data('nDims', nDims)
        self.data_info.set_meta_data('axis_labels', axis_labels)
        # if parameter tuning
        if self._get_plugin_data().multi_params_dict:
            self.__add_extra_dims_labels()

    def __add_extra_dims_labels(self):
        """ Add axis labels to extra dimensions created by parameter tuning. 
        """
        params_dict = self._get_plugin_data().multi_params_dict
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
        """ Helper function to remove, replace/add or insert axis_labels into
        existing axis_labels
        """
        removed_dims = 0
        for arg in args[0]:
            if len(arg.split('.')) is 1:
                self.__remove_axis_labels(arg, removed_dims)
                removed_dims += 1
            else:
                if len(arg.split('~')) is 1:
                    self.__replace_axis_labels(arg)
                else:
                    self.__insert_axis_labels(arg)

    def __remove_axis_labels(self, label, removed_dims):
        """ Remove axis labels. """
        axis_labels = self.get_axis_labels()
        del axis_labels[int(label) - removed_dims]
        self.data_info.set_meta_data(
            'nDims', self.data_info.get_meta_data('nDims') - 1)

    def __replace_axis_labels(self, label):
        """ Replace or add axis labels. """
        axis_labels = self.get_axis_labels()
        label = label.split('.')
        axis_labels[int(label[0])] = {label[1]: label[2]}
        if int(label[0]) > self.data_info.get_meta_data('nDims'):
            self.data_info.set_meta_data(
                'nDims', self.data_info.get_meta_data('nDims') + 1)

    def __insert_axis_labels(self, label):
        """ Insert axis labels. """
        axis_labels = self.get_axis_labels()
        label = label.split('~')[1].split('.')
        axis_labels.insert(int(label[0]), {label[1]: label[2]})
        self.data_info.set_meta_data(
            'nDims', self.data_info.get_meta_data('nDims') + 1)

    def __set_data_patterns(self, patterns):
        """ Add missing dimensions to patterns and populate data info dict. """
        all_dims = range(len(self.get_shape()))
        for p in patterns:
            pDims = patterns[p]['core_dir'] + patterns[p]['slice_dir']
            for dim in all_dims:
                if dim not in pDims:
                    patterns[p]['slice_dir'] += (dim,)
        self.data_info.set_meta_data('data_patterns', patterns)

    def __find_and_set_shape(self, data):
        """ Add any extra dimensions, from parameter tuning, to the shape and
        set the shape in the framework. """
        pData = self._get_plugin_data()
        new_shape = copy.copy(data.get_shape()) + tuple(pData.extra_dims)
        self.set_shape(new_shape)
