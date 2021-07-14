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
.. module:: stitch_data
   :platform: Unix
   :synopsis: A module for stitching together multiple datasets.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.data.data_structures.data_types.base_type import BaseType


class StitchData(BaseType):
    """ This class is used to combine multiple data objects. """

    def __init__(self, data_obj_list, stack_or_cat, dim, remove=[]):
        self.obj_list = data_obj_list
        self.dtype = data_obj_list[0].data.dtype
        self.stack_or_cat = stack_or_cat
        self.dim = dim
        self.remove = remove
        self.dark_updated = False
        self.flat_updated = False
        super(StitchData, self).__init__()

        self.shape = None
        self._set_shape()
        if self.stack_or_cat == 'stack':
            self.inc = 1
            self._getitem = self._getitem_stack
            self._get_lists = self._get_lists_stack
        else:
            self.inc = self.obj_list[0].get_shape()[self.dim]
            self._getitem = self._getitem_cat
            self._get_lists = self._get_lists_cat

    def clone_data_args(self, args, kwargs, extras):
        args = ['obj_list', 'stack_or_cat', 'dim']
        kwargs['remove'] = 'remove'
        extras = ['shape']
        return args, kwargs, extras

    def __getitem__(self, idx):
        size = [len(np.arange(s.start, s.stop, s.step)) for s in idx]
        obj_list, in_slice_list, out_slice_list = self._get_lists(idx)
        data = np.empty(size)

        for i in range(len(obj_list)):
            data[tuple(out_slice_list[i])] = \
                self._getitem(obj_list[i], in_slice_list[i])
        return data

    def _getitem_stack(self, obj, sl):
        data = obj.data[tuple(sl)]
        for i in np.sort(self.remove)[::-1]:
            data = np.squeeze(data, axis=i)
        return np.expand_dims(data, self.dim)

    def _getitem_cat(self, obj, sl):
        data = obj.data[tuple(sl)]
        for i in np.sort(self.remove)[::-1]:
            data = np.squeeze(data, axis=i)
        return data

    def _get_lists_stack(self, idx):
        entry = idx[self.dim]
        init_vals = np.arange(entry.start, entry.stop, entry.step)
        obj_list = []
        for i in init_vals:
            obj_list.append(self.obj_list[i])

        in_idx = list(idx)
        del in_idx[self.dim]
        in_slice_list = np.tile(in_idx, (len(init_vals), 1))

        out_slice_list = \
            [slice(0, len(np.arange(s.start, s.stop, s.step))) for s in idx]
        out_slice_list = np.tile(out_slice_list, (len(init_vals), 1))

        new_slices = [slice(i, i + 1) for i in range(len(init_vals))]
        out_slice_list[:, self.dim] = new_slices
        return obj_list, in_slice_list, out_slice_list

    def _get_lists_cat(self, idx):
        inc = self.inc
        entry = idx[self.dim]
        init_vals = np.arange(entry.start, entry.stop, entry.step)
        array = init_vals % inc
        index = np.where(np.diff(array) < 0)[0] + 1

        val_list = np.array_split(array, index)
        obj_vals = init_vals[np.append(0, index)] / inc
        active_obj_list = []
        for i in obj_vals:
            active_obj_list.append(self.obj_list[i])

        in_slice_list = self._set_in_slice_list(idx, val_list, entry)
        out_slice_list = self._set_out_slice_list(idx, val_list)
        return active_obj_list, in_slice_list, out_slice_list

    def _set_in_slice_list(self, idx, val_list, entry):
        in_slice_list = np.tile(idx, (len(val_list), 1))
        new_slices = [slice(e[0], e[-1] + 1, entry.step) for e in val_list]
        in_slice_list[:, self.dim] = new_slices
        return in_slice_list

    def _set_out_slice_list(self, idx, val_list):
        out_slice_list = \
            [slice(0, len(np.arange(s.start, s.stop, s.step))) for s in idx]
        out_slice_list = np.tile(out_slice_list, (len(val_list), 1))
        length = np.append(0, np.cumsum([len(v) for v in val_list]))
        if self.stack_or_cat == 'cat':
            new_slices = \
                [slice(length[i - 1], length[i])
                 for i in range(1, len(length))]
        else:
            new_slices = [slice(i, i + 1) for i in range(len(val_list))]
        out_slice_list[:, self.dim] = new_slices
        return out_slice_list

    def get_shape(self):
        return self.shape

    def _set_shape(self):
        nObjs = len(self.obj_list)
        shape = list(self.obj_list[0].data.shape)

        for dim in np.sort(self.remove)[::-1]:
            del shape[dim]

        if self.stack_or_cat == 'cat':
            shape[self.dim] *= nObjs
        else:
            shape.insert(self.dim, nObjs)
        self.shape = tuple(shape)

    def update_dark(self, data):
        self.dark_updated = data

    def update_flat(self, data):
        self.flat_updated = data

    def dark(self):
        if self.dark_updated:
            return self.dark_updated
        if self.stack_or_cat == 'stack':
            return np.vstack(tuple(np.asarray([d.data.dark() for d in self.obj_list])))
        else:
            return np.hstack(tuple(np.asarray([d.data.dark() for d in self.obj_list])))

    def flat(self):
        if self.flat_updated:
            return self.flat_updated
        if self.stack_or_cat == 'stack':
            return np.vstack(tuple(np.asarray([d.data.flat() for d in self.obj_list])))
        else:
            return np.hstack(tuple(np.asarray([d.data.flat() for d in self.obj_list])))

    def dark_mean(self):
        """ Get the averaged dark projection data. """
        if self.stack_or_cat == 'stack':
            return np.vstack(tuple(np.asarray([d.data.dark_mean() for d in self.obj_list])))
        else:
            return np.hstack(tuple(np.asarray([d.data.dark_mean() for d in self.obj_list])))

    def flat_mean(self):
        """ Get the averaged flat projection data. """
        if self.stack_or_cat == 'stack':
            return np.vstack(tuple(np.asarray([d.data.flat_mean() for d in self.obj_list])))
        else:
            return np.hstack(tuple(np.asarray([d.data.flat_mean() for d in self.obj_list])))
