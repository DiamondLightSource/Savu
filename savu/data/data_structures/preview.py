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
.. module:: preview
   :platform: Unix
   :synopsis: This class deals with previewing (reduction) of the data and is\
   encapsulated in the Data class.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""
import numpy as np

import savu.data.data_structures.data_notes as notes
from savu.core.utils import docstring_parameter


class Preview(object):
    """The Data class dynamically inherits from transport specific data class
    and holds the data array, along with associated information.
    """
    def __init__(self, data_obj):
        self._data_obj = data_obj
        self.revert_shape = None

    def get_data_obj(self):
        return self._data_obj

    @docstring_parameter(notes._set_preview_note.__doc__)
    def set_preview(self, preview_list, **kwargs):
        """ Reduces the data to be processed to a subset of the original.

        :param list preview: previewing parameters, where
            ``len(preview_list)`` equals the number of data dimensions.
        :keyword bool revert: revert input dataset to the original size after
         plugin processing.

        {0}
        """
        self.revert_shape = kwargs.get('revert', self.revert_shape)
        shape = self.get_data_obj().get_shape()
        if preview_list:
            preview_list = self.__add_preview_defaults(preview_list)
            starts, stops, steps, chunks = \
                self.__get_preview_indices(preview_list)
            shape_change = True
        else:
            starts, stops, steps, chunks = \
                [[0]*len(shape), shape, [1]*len(shape), [1]*len(shape)]
            shape_change = False
        self.__set_starts_stops_steps(starts, stops, steps, chunks,
                                      shapeChange=shape_change)
        self.__check_preview_indices()

    def __add_preview_defaults(self, plist):
        """ Fill in missing values in preview list entries.

        :param: preview list with entries of the form
            ``start[:stop:step:chunk]``
        :returns: preview list with missing values replaced by defaults
        :rtype: list
        """
        nEntries = 4
        diff_len = [(nEntries - len(elem.split(':'))) for elem in plist]
        diff3 = [i for i in range(len(diff_len)) if diff_len[i] is 3]
        for dim in diff3:
            plist[dim] = plist[dim] + ':' + plist[dim] + '+1'
            diff_len[dim] = 2

        all_idx = [i for i in range(len(plist)) if plist[i] == ':']
        amend = [i for i in range(len(plist)) if diff_len and i not in all_idx]
        for idx in amend:
            plist[idx] += ':1'*diff_len[idx]
        return plist

    def _unset_preview(self):
        """ Unset preview (revert=True) if it was only required in the plugin.
        """
        self._data_obj.set_shape(self.revert_shape)
        self.set_preview([])
        self.revert_shape = None

    def __set_starts_stops_steps(self, starts, stops, steps, chunks,
                                 shapeChange=True):
        """ Add previewing params to data_info dictionary and set reduced
        shape.
        """
        set_mData = self.get_data_obj().data_info.set_meta_data
        set_mData('starts', starts)
        set_mData('stops', stops)
        set_mData('steps', steps)
        set_mData('chunks', chunks)
        if shapeChange:
            self.__set_reduced_shape(starts, stops, steps, chunks)
            self.__apply_previewing_to_axis_labels(
            starts, stops, steps, chunks)

    def __get_preview_indices(self, preview_list):
        """ Get preview_list ``starts``, ``stops``, ``steps``, ``chunks``
        separate components with integer values.

        :params: preview_list
        :returns: separate list of starts, stops, steps, chunks integer values
        :rtype: list(list(int))
        """
        starts = len(preview_list)*[None]
        stops = len(preview_list)*[None]
        steps = len(preview_list)*[None]
        chunks = len(preview_list)*[None]

        for i in range(len(preview_list)):
            if preview_list[i] is ':':
                preview_list[i] = '0:end:1:1'
            vals = preview_list[i].split(':')
            starts[i], stops[i], steps[i], chunks[i] = \
                self.__convert_indices(vals, i)
        return starts, stops, steps, chunks

    def __convert_indices(self, idx, dim):
        """ convert keywords to integers.
        """
        dobj = self.get_data_obj()
        shape = dobj.get_shape()
        mid = shape[dim]/2 - 1
        end = shape[dim]
        idx = [eval(equ) for equ in idx]
        idx = [idx[i] if idx[i] > -1 else shape[dim]+1+idx[i] for i in
               range(len(idx))]
        return idx

    def get_starts_stops_steps(self, key=None):
        """ Returns preview parameter ``starts``, ``stops``, ``steps``,
        ``chunks`` lists.

        :keyword str key: the list to return.
        :returns: if key is none return  separate preview_list components,
         where each list has length equal to number of dataset dimensions, else
         only the ``key`` list.
        :rtype: list(list(int))
        """
        get_mData = self.get_data_obj().data_info.get_meta_data
        if key is not None:
            return get_mData(key)
        else:
            starts = get_mData('starts')
            stops = get_mData('stops')
            steps = get_mData('steps')
            chunks = get_mData('chunks')
            return starts, stops, steps, chunks

    def __check_preview_indices(self):
        starts, stops, steps, chunks = self.get_starts_stops_steps()
        nDims = len(starts)
        for i in range(nDims):
            if stops[i] <= starts[i]:
                raise Exception("Error in previewing parameters!")

    def __set_reduced_shape(self, starts, stops, steps, chunks):
        """ Set new shape if data is reduced by previewing.
        """
        dobj = self.get_data_obj()
        orig_shape = dobj.get_shape()
        dobj.data_info.set_meta_data('orig_shape', orig_shape)
        new_shape = []
        for dim in range(len(starts)):
            new_shape.append(np.prod((dobj._get_slice_dir_matrix(dim).shape)))
        dobj.set_shape(tuple(new_shape))

    def __apply_previewing_to_axis_labels(self, starts, stops, steps, chunks):
        """ Amend the axis label values based on the previewing parameters.
        """
        dobj = self.get_data_obj()
        slice_list = []
        for dim in range(len(dobj.get_shape())):
            if chunks[dim] > 1:
                slice_list.append(
                    np.ravel(np.transpose(dobj._get_slice_dir_matrix(dim))))
            else:
                slice_list.append(
                    np.arange(starts[dim], stops[dim], steps[dim]))
        dobj.amend_axis_label_values(slice_list)
