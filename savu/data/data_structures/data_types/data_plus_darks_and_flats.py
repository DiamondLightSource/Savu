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
.. module:: data_with_darks_and_flats
   :platform: Unix
   :synopsis: A class for loading data that has associated dark and flat \
       fields.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
import copy

from savu.data.data_structures.data_types.base_type import BaseType


class DataWithDarksAndFlats(BaseType):

    def __init__(self, data_obj, proj_dim, image_key):
        super(DataWithDarksAndFlats, self).__init__()
        self.fscale = 1
        self.dscale = 1
        self.flat_updated = False
        self.dark_updated = False
        self.data = data_obj.data
        self.dark_flat_slice_list = []
        self.dtype = data_obj.data.dtype

    def _base_extra_params(self):
        """ global class parameter names that are updated outside of __init__
        """
        extras = ['fscale', 'dscale', 'dark_updated', 'flat_updated',
                  'dark_flat_slice_list']
        return extras

    def _override_data_type(self, data):
        self.data = data

    def get_image_key(self):
        preview_sl = self.data_obj.get_preview()._get_preview_slice_list()
        if preview_sl is None:
            return self.image_key
        return self.__get_preview_image_key(preview_sl[self.proj_dim])

    def _get_image_key_data_shape(self):
        data_idx = self.get_index(0)
        new_shape = list(self.data.shape)
        new_shape[self.proj_dim] = len(data_idx)
        return tuple(new_shape)

    def _getitem_imagekey(self, idx):
        index = list(idx)
        index[self.proj_dim] = \
            self.get_index(0, full=True)[idx[self.proj_dim]].tolist()
        return self.data[tuple(index)]

    def _getitem_noimagekey(self, idx):
        return self.data[idx]

    def __setitem__(self, key, val):
        self.data[key] = val

    def get_dark_flat_slice_list(self):
        slice_list = self.data_obj._preview._get_preview_slice_list()
        remove_dim = \
            self.data_obj.get_data_dimension_by_axis_label('rotation_angle')
        slice_list[remove_dim] = slice(None)

        if len(slice_list) > 3:
            idx = np.arange(0, len(slice_list))
            detX = self.data_obj.get_data_dimension_by_axis_label('detector_x')
            detY = self.data_obj.get_data_dimension_by_axis_label('detector_y')
            remove = set(idx).difference({remove_dim, detX, detY})
            for dim in sorted(list(remove), reverse=True):
                del slice_list[dim]

        return slice_list

    def _set_scale(self, name, scale):
        self.set_flat_scale(scale) if name == 'flat' else \
            self.set_dark_scale(scale)

    def set_flat_scale(self, fscale):
        self.fscale = float(fscale)

    def set_dark_scale(self, dscale):
        self.dscale = float(dscale)

    def get_shape(self):
        return self.shape

    def dark_mean(self):
        """ Get the averaged dark projection data. """
        return self._calc_mean(self.dark())

    def flat_mean(self):
        """ Get the averaged flat projection data. """
        return self._calc_mean(self.flat())

    def _calc_mean(self, data):
        return data if len(data.shape) == 2 else \
            data.mean(self.proj_dim).astype(np.float32)

    def get_index(self, key, full=False):
        """ Get the projection index of a specific image key value.

        :params int key: the image key value
        """
        if full is True:
            return np.where(self.image_key == key)[0]
        else:
            return self.__get_preview_index(key)

    def __get_preview_index(self, key):
        # Remove this try/except statement
        preview_sl = self.data_obj.get_preview()._get_preview_slice_list()
        if preview_sl is None:
            return np.where(self.image_key == key)[0]
        else:
            return self.__get_reduced_index(key, preview_sl[self.proj_dim])

    def __get_preview_image_key(self, slice_list):
        # all data entries
        data_idx = np.where(self.image_key == 0)[0]
        preview_idx = np.arange(len(data_idx))[slice_list]
        # check the inconsistency regarding the preview of angles, e.g [0:10,:,:]
        if len(data_idx) == len(preview_idx):
            remove_idx = np.delete(data_idx, preview_idx[::-1])
        else:
            remove_idx = []
        return np.delete(self.image_key, remove_idx)

    def __get_reduced_index(self, key, slice_list):
        """ Get the projection index of a specific image key value when\
            previewing has been applied. """
        preview_image_key = self.__get_preview_image_key(slice_list)
        return np.where(preview_image_key == key)[0]

    def __get_data(self, key):
        index = [slice(None)] * self.nDims
        rot_dim = self.data_obj.get_data_dimension_by_axis_label(
            'rotation_angle')

        # separate the transfer of data for slice lists with entries far \
        # apart, as this significantly improves hdf5 performance.
        split_diff = 10
        k_idx = self.get_index(key)
        if not k_idx.size:
            return np.array([])

        k_idx = np.split(k_idx, np.where(np.diff(k_idx) > split_diff)[0] + 1)

        index[self.proj_dim] = k_idx[0]
        data = self.data[tuple(index)]

        for idx in k_idx[1:]:
            index[self.proj_dim] = idx
            data = np.append(data, self.data[tuple(index)], axis=rot_dim)

        if not self.dark_flat_slice_list[key]:
            return data

        sl = list(copy.deepcopy(self.dark_flat_slice_list[key]))
        if len(data.shape) == 2:
            del sl[rot_dim]
        return data[tuple(sl)]

    def dark_image_key_data(self):
        """ Get the dark data. """
        return self.__get_data(2) * self.dscale

    def flat_image_key_data(self):
        """ Get the flat data. """
        return self.__get_data(1) * self.fscale

    def update_dark(self, data):
        self.dark_updated = data
        self.dscale = 1
        self.dark_flat_slice_list[2] = None
        self.data_obj.meta_data.set('dark', self._calc_mean(data))

    def update_flat(self, data):
        self.flat_updated = data
        self.fscale = 1
        self.dark_flat_slice_list[1] = None
        self.data_obj.meta_data.set('flat', self._calc_mean(data))

    def _set_dark_and_flat(self):
        slice_list = self.data_obj._preview._get_preview_slice_list()
        if slice_list:
            self.dark_flat_slice_list = \
                [tuple(self.get_dark_flat_slice_list())] * 3


class ImageKey(DataWithDarksAndFlats):
    """ This class is used to get data from a dataset with an image key. """

    def __init__(self, data_obj, image_key, proj_dim, ignore=None):
        self.data_obj = data_obj
        self.image_key = image_key
        self.proj_dim = proj_dim
        self.ignore = ignore
        super(ImageKey, self).__init__(data_obj, proj_dim, image_key)
        self.shape = self._get_image_key_data_shape()
        self.nDims = len(self.shape)
        self._getitem = self._getitem_imagekey
        if ignore:
            self.__ignore_image_key_entries(ignore)

    def clone_data_args(self, args, kwargs, extras):
        """ List the arguments required to clone this datatype
        """
        args = ['self', 'image_key', 'proj_dim']
        kwargs['ignore'] = 'ignore'
        extras = self._base_extra_params()
        return args, kwargs, extras

    def map_input_args(self, args, kwargs, cls, extras):
        """ List all information required to keep this data set after a plugin
        has completed (may require conversion to another type)
        """
        args = ['self', None, 'proj_dim']
        kwargs['dark'] = 'dark'
        kwargs['flat'] = 'flat'
        extras = self._base_extra_params()
        cls = NoImageKey.__module__ + '.NoImageKey'
        return args, kwargs, cls, extras

    def _finish_cloning(self):
        self.dark_flat_slice_list[0] = None

    def __getitem__(self, idx):
        return self._getitem(idx)

    def __ignore_image_key_entries(self, ignore):
        a, a, start, end = self._get_start_end_idx(self.get_index(1))
        if not isinstance(ignore, list):
            ignore = [ignore]
        for batch in ignore:
            self.image_key[start[batch - 1]:end[batch - 1] + 1] = 3

    def dark(self):
        """ Get the dark data. """
        return self.dark_updated if self.dark_updated is not False else \
            self.dark_image_key_data()

    def flat(self):
        """ Get the flat data. """
        return self.flat_updated if self.flat_updated is not False else \
            self.flat_image_key_data()


class NoImageKey(DataWithDarksAndFlats):
    """ This class is used to get data from a dataset with separate darks and
        flats. """

    def __init__(self, data_obj, image_key, proj_dim, dark=None, flat=None):
        self.data_obj = data_obj
        self.image_key = image_key
        self.proj_dim = proj_dim
        super(NoImageKey, self).__init__(data_obj, proj_dim, image_key)
        self.dark_path = dark
        self.flat_path = flat
        self.orig_image_key = copy.copy(image_key)
        self.flat_image_key = []
        self.dark_image_key = []

        # darks and flats belong to another dataset with an image key
        if self.image_key is not None:
            self.shape = self._get_image_key_data_shape()
            self._getitem = self._getitem_imagekey
        else:
            self.shape = data_obj.data.shape
            self._getitem = self._getitem_noimagekey

        self.data_obj = data_obj
        self.nDims = len(self.shape)

    def clone_data_args(self, args, kwargs, extras):
        # these are the arguments required when creating a class instance
        args = ['self', 'image_key', 'proj_dim']  # always 'self goes first'
        kwargs['dark'] = 'dark_path'
        kwargs['flat'] = 'flat_path'
        # global class parameter names that are updated outside of __init__
        extras = ['image_key', 'flat_image_key', 'flat_path',
                  'dark_image_key', 'dark_path'] + self._base_extra_params()
        return args, kwargs, extras

    def __getitem__(self, idx):
        return self._getitem(idx)

    def _post_clone_updates(self):
        self.dark_flat_slice_list[0] = None

    def _set_fake_key(self, fakekey):
        # useful if the darks and flats did belong to data with an
        # image key in a previous plugin
        self.image_key = fakekey

    def _set_flat_path(self, path, imagekey=[]):
        self.flat_image_key = imagekey
        self.flat_path = path

    def _set_dark_path(self, path, imagekey=[]):
        self.dark_image_key = imagekey
        self.dark_path = path

    def get_shape(self):
        return self.shape

    def dark(self):
        """ Get the dark data. """
        if self.dark_updated is not False:
            return self.dark_updated
        if len(self.dark_image_key) > 0:
            self.image_key = self.dark_image_key
            dark = self.dark_image_key_data()
            self.image_key = self.orig_image_key
            return dark
        return self.dark_path[self.dark_flat_slice_list[2]] * self.dscale

    def flat(self):
        """ Get the flat data. """
        if self.flat_updated is not False:
            return self.flat_updated
        if len(self.flat_image_key) > 0:
            self.image_key = self.flat_image_key
            flat = self.flat_image_key_data()
            self.image_key = self.orig_image_key
            return flat
        return self.flat_path[self.dark_flat_slice_list[1]] * self.fscale
