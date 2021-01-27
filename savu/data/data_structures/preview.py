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

from savu.core.utils import docstring_parameter
from savu.plugins.utils import parse_config_string as parse_str
import savu.data.data_structures.data_notes as notes


class Preview(object):
    """The Data class dynamically inherits from transport specific data class
    and holds the data array, along with associated information.
    """
    def __init__(self, data_obj):
        self._data_obj = data_obj
        self.revert_shape = None
        self.revert_axis_labels = None
        self.plugin_preview = None

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
        load = kwargs.get('load', False)
        shape = self.get_data_obj().get_shape()
        # for backward compatibility
        preview_list = parse_str(preview_list) if \
            isinstance(preview_list, str) else preview_list
        preview_list = self.__convert_nprocs(preview_list)

        if preview_list:
            preview_list = self._add_preview_defaults(preview_list)
            starts, stops, steps, chunks = \
                self._get_preview_indices(preview_list)
            shape_change = True
        else:
            starts, stops, steps, chunks = \
                [[0]*len(shape), shape, [1]*len(shape), [1]*len(shape)]
            shape_change = False

        self.__set_starts_stops_steps(starts, stops, steps, chunks,
                                      shapeChange=shape_change, load=load)
        self.__check_preview_indices()

    def __convert_nprocs(self, preview_list):
        for i in range(len(preview_list)):
            if preview_list[i] == 'nprocs':
                nprocs = self.get_data_obj().exp.meta_data.get('nProcesses')
                start = int(np.floor(nprocs / 2.0))
                end = int(np.ceil(nprocs / 2.0))
                preview_list[i] = f'mid-{start}:mid-{end}'
        return preview_list

    def _add_preview_defaults(self, plist):
        """ Fill in missing values in preview list entries.

        :param: preview list with entries of the form
            ``start[:stop:step:chunk]``
        :returns: preview list with missing values replaced by defaults
        :rtype: list
        """
        nEntries = 4
        #plist = [str(i) for i in plist] if isinstance(plist[0], int) else plist
        plist = [str(i) if isinstance(i, int) else i for i in plist]
        diff_len = [(nEntries - len(elem.split(':'))) for elem in plist]
        diff3 = [i for i in range(len(diff_len)) if diff_len[i] == 3]
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

    def _reset_preview(self):
        self.set_preview([])
        self.plugin_preview = None

    def __set_starts_stops_steps(self, starts, stops, steps, chunks,
                                 shapeChange=True, load=False):
        """ Add previewing params to data_info dictionary and set reduced
        shape.
        """

        set_mData = self.get_data_obj().data_info.set
        set_mData('starts', starts)
        set_mData('stops', stops)
        set_mData('steps', steps)
        set_mData('chunks', chunks)
        if shapeChange:
            self.__set_reduced_shape(starts, stops, steps, chunks)
            slice_list = self._get_preview_slice_list()
            self.get_data_obj().amend_axis_label_values(slice_list)
        if load:
            self.__add_preview_param('starts', starts)
            self.__add_preview_param('stops', stops)
            self.__add_preview_param('steps', steps)

    def __add_preview_param(self, name, value):
        entry = self.get_data_obj().get_name() + '_preview_' + name
        self.get_data_obj().exp.meta_data.set(entry, value)

    def _get_preview_indices(self, preview_list):
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
            if preview_list[i] == ':':
                preview_list[i] = '0:end:1:1'
            vals = preview_list[i].split(':')
            starts[i], stops[i], steps[i], chunks[i] = \
                self.convert_indices(vals, i)

        return starts, stops, steps, chunks

    def get_integer_entries(self, plist):
        """
        Convert Savu preview syntax to python slicing (similar) syntax, by
        replacing Savu Built-in constants.
        
        Parameters
        ----------
        plist : list
            A Savu data preview list to reduce the data dimensions.

        Returns
        -------
        list
            A Savu preview list containing integers and no strings.

        """
        if plist:
            vals = self._get_preview_indices(self._add_preview_defaults(plist))
        else:
            shape = self.get_data_obj().get_shape()
            vals = [[0]*len(shape), shape, [1]*len(shape), [1]*len(shape)]        
        return [':'.join(map(str, l)) for l in list(zip(*vals))]

    def convert_indices(self, idx, dim):
        """ convert keywords to integers.
        """
        dobj = self.get_data_obj()
        shape = dobj.get_shape()
        mid = np.clip(np.ceil(shape[dim] / 2.0).astype('int') - 1, 0, None)
        end = shape[dim]
        idx = [eval(equ, {"builtins": None}, {'mid': mid, 'end': end}) for equ in idx]
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
        mData = self.get_data_obj().data_info

        if 'starts' not in list(mData.get_dictionary().keys()):
            return None if key else [None]*4

        if key is not None:
            return mData.get(key)

        return [mData.get('starts'), mData.get('stops'), mData.get('steps'),
                mData.get('chunks')]

    def __check_preview_indices(self):
        starts, stops, steps, chunks = self.get_starts_stops_steps()
        nDims = len(starts)
        for i in range(nDims):
            if stops[i] <= starts[i]:
                raise Exception("Error in previewing parameters! "
                                "Check parameters that may alter data dimensions. "
                                "(axis={}, start={}, stop={})".format(
                                    i, starts[i], stops[i]))

    def __set_reduced_shape(self, starts, stops, steps, chunks):
        """ Set new shape if data is reduced by previewing.
        """
        dobj = self.get_data_obj()
        td = dobj._get_transport_data()
        orig_shape = dobj.get_shape()
        dobj.data_info.set('orig_shape', orig_shape)
        new_shape = []
        for dim in range(len(starts)):
            new_shape.append(np.prod((td._get_slice_dir_matrix(dim).shape)))
        dobj.set_shape(tuple(new_shape))

    def _get_preview_slice_list(self):
        """ Amend the axis label values based on the previewing parameters.
        """
        dobj = self.get_data_obj()
        td = dobj._get_transport_data()
        starts, stops, steps, chunks = self.get_starts_stops_steps()

        if starts is None:
            return None

        slice_list = []
        for dim in range(len(dobj.get_shape())):
            if chunks[dim] > 1:
                slice_list.append(
                    np.ravel(np.transpose(td._get_slice_dir_matrix(dim))))
            else:
                slice_list.append(slice(starts[dim], stops[dim], steps[dim]))
        return slice_list
