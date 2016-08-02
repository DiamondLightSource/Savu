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
.. module:: data_type
   :platform: Unix
   :synopsis: A module containing classes for different input data types other
       than hdf5.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import numpy as np
import fabio
import copy


class DataTypes(object):

    def __getitem__(self, index):
        """ Override __getitem__ and map to the relevant files """
        raise NotImplementedError("__getitem__ must be implemented.")

    def get_shape(self):
        """ Get full stiched shape of a stack of files"""
        raise NotImplementedError("get_shape must be implemented.")

    def add_base_class_with_instance(self, base, inst):
        """ Add a base class instance to a class (merging of two data types).

        :params class base: a class to add as a base class
        :params instance inst: a instance of the base class
        """
        cls = self.__class__
        namespace = self.__class__.__dict__.copy()
        self.__dict__.update(inst.__dict__)
        self.__class__ = cls.__class__(cls.__name__, (cls, base), namespace)


class FabIO(DataTypes):
    """ This class loads any of the FabIO python module supported image
    formats. """

    def __init__(self, folder, Data, dim, shape=None, data_prefix=None):
        self._data_obj = Data
        self.nFrames = None
        self.start_file = fabio.open(self.__get_file_name(folder, data_prefix))
        self.frame_dim = dim
        self.image_shape = (self.start_file.dim2, self.start_file.dim1)
        if shape is None:
            self.shape = (self.nFrames,)
        else:
            self.shape = shape

    def __getitem__(self, index):
        size = [len(np.arange(i.start, i.stop, i.step)) for i in index]
        data = np.empty(size)
        tiffidx = [i for i in range(len(index)) if i not in self.frame_dim]
        tiff_slices = [index[i] for i in tiffidx]

        # shift tiff dims to start from 0
        index = list(index)
        for i in tiffidx:
            if index[i].start is not 0:
                index[i] = slice(0, index[i].stop - index[i].start)

        index, frameidx = self.__get_indices(index, size)

        for i in range(len(frameidx)):
            data[index[i]] = self.start_file.getframe(
                self.start_no + frameidx[i]).data[tiff_slices]
        return data

    def __get_file_name(self, folder, prefix):
        import re
        import glob
#        files = os.listdir(folder)
        fullpath = str.strip(folder)
        if prefix != None:
            fullpath = os.path.join(folder, prefix)
        fullpath += "*"
        files = glob.glob(fullpath)
        self.nFrames = len(files)
        fname = sorted(files)[0]
        self.start_no = [int(s) for s in re.findall(r'\d+', fname)][-1]
        return fname
#        return folder + "/" + fname

    def get_shape(self):
        return self.shape + self.image_shape

    def __get_idx(self, dim, sl, shape):
        c = int(np.prod(shape[0:dim]))
        r = int(np.prod(shape[dim+1:]))
        values = np.arange(sl.start, sl.stop, sl.step)
        return np.ravel(np.kron(values, np.ones((r, c))))

    def __get_indices(self, index, size):
        """ Get the indices for the new data array and the file numbers. """
        sub_idx = np.array(index)[np.array(self.frame_dim)]
        sub_size = [size[i] for i in self.frame_dim]

        idx_list = []
        for dim in range(len(sub_idx)):
            idx = self.__get_idx(dim, sub_idx[dim], sub_size)
            idx_list.append(idx.astype(int))

        lshape = idx_list[0].shape[0]
        index = np.tile(index, (lshape, 1))
        frameidx = np.zeros(lshape)

        for dim in range(len(sub_idx)):
            start = index[0][self.frame_dim[dim]].start
            index[:, self.frame_dim[dim]] = \
                [slice(i-start, i-start+1, 1) for i in idx_list[dim]]
            frameidx[:] += idx_list[dim]*np.prod(self.shape[dim+1:])
        return index.tolist(), frameidx.astype(int)


class Map_3dto4d_h5(DataTypes):
    """ This class converts a 3D dataset to a 4D dataset. """

    def __init__(self, data, n_angles):
        shape = data.shape

        import inspect
        if inspect.isclass(type(data)):
            self.add_base_class_with_instance(type(data), data)

        self.data = data
        new_shape = (n_angles, shape[1], shape[2], shape[0]/n_angles)
        self.shape = new_shape

    def __getitem__(self, idx):
        n_angles = self.shape[0]
        idx_dim3 = np.arange(idx[3].start, idx[3].stop, idx[3].step)
        idx_dim0 = np.arange(idx[0].start, idx[0].stop, idx[0].step)
        idx_dim0 = np.ravel(idx_dim3.reshape(-1, 1)*n_angles + idx_dim0)

        size = [len(np.arange(i.start, i.stop, i.step)) for i in idx]
        data = np.empty(size)

        change = np.where(idx_dim0[:-1]/n_angles != idx_dim0[1:]/n_angles)[0]
        start = idx_dim0[np.append(0, change+1)]
        stop = idx_dim0[np.append(change, len(idx_dim0)-1)] + 1
        length = stop - start

        for i in range(len(start)):
            new_slice = [slice(start[i], stop[i], idx[0].step), idx[1], idx[2]]
            data[0:length[i], :, :, i] = self.data[tuple(new_slice)]
        return data

    def get_shape(self):
        return self.shape


class Tomo(DataTypes):

    def __init__(self, data_obj, proj_dim, image_key):
        self.data_obj = data_obj
        self.fscale = 1
        self.dscale = 1
        self.flat_updated = False
        self.dark_updated = False
        self.image_key = image_key
        self.data = data_obj.data
        self.proj_dim = proj_dim
        self.dark_flat_slice_list = None

    def _copy_base(self, new_obj):
        new_obj.flat_updated = self.flat_updated
        new_obj.dark_updated = self.dark_updated
        self._set_dark_and_flat()

    def get_image_key(self):
        return self.image_key

    def _get_image_key_data_shape(self):
        data_idx = self.get_index(0)
        new_shape = list(self.data.shape)
        new_shape[self.proj_dim] = len(data_idx)
        return tuple(new_shape)

    def _getitem_imagekey(self, idx):
        index = list(idx)
        index[self.proj_dim] = self.get_index(0)[idx[self.proj_dim]].tolist()
        return self.data[tuple(index)]

    def _getitem_noimagekey(self, idx):
        return self.data[idx]

    def __setitem__(self, key, val):
        self.data[key] = val

    def _set_dark_and_flat(self):
        self.dark_flat_slice_list = self.get_dark_flat_slice_list()

        # remove extra dimension if 3d to 4d mapping
        from data_type import Map_3dto4d_h5
        if Map_3dto4d_h5 in self.__class__.__bases__:
            del self.dark_flat_slice_list[-1]

        self.dark_flat_slice_list = tuple(self.dark_flat_slice_list)
        self.data_obj.meta_data.set_meta_data('dark', self.dark_mean())
        self.data_obj.meta_data.set_meta_data('flat', self.flat_mean())

    def get_dark_flat_slice_list(self):
        slice_list = self.data_obj._preview._get_preview_slice_list()
        remove_dim = self.data_obj.find_axis_label_dimension('rotation_angle')
        slice_list[remove_dim] = slice(None)
        return slice_list

    def _set_scale(self, name, scale):
        self.set_flat_scale(scale) if name is 'flat' else\
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
        return data if len(data.shape) is 2 else\
            data.mean(self.proj_dim).astype(np.float32)

    def get_index(self, key):
        """ Get the projection index of a specific image key value.

        :params int key: the image key value
        """
        return np.where(self.image_key == key)[0]

    def __get_data(self, key):
        index = [slice(None)]*self.nDims
        index[self.proj_dim] = self.get_index(key)
        data = self.data[tuple(index)]
        return data[self.dark_flat_slice_list]

    def dark_image_key_data(self):
        """ Get the dark data. """
        return self.__get_data(2)*self.dscale

    def flat_image_key_data(self):
        """ Get the flat data. """
        return self.__get_data(1)*self.fscale

    def update_dark(self, data):
        self.dark_updated = data
        self.dscale = 1
        self.data_obj.meta_data.set_meta_data('dark', self._calc_mean(data))

    def update_flat(self, data):
        self.flat_updated = data
        self.fscale = 1
        self.data_obj.meta_data.set_meta_data('flat', self._calc_mean(data))


class ImageKey(Tomo):
    """ This class is used to get data from a dataset with an image key. """

    def __init__(self, data_obj, image_key, proj_dim):
        super(ImageKey, self).__init__(data_obj, proj_dim, image_key)
        self.shape = self._get_image_key_data_shape()
        self.nDims = len(self.shape)
        self._getitem = self._getitem_imagekey

    def __getitem__(self, idx):
        return self._getitem(idx)

    def _copy(self, new_obj):
        self._copy_base(new_obj)

    def dark(self):
        """ Get the dark data. """
        return self.dark_updated if self.dark_updated else\
            self.dark_image_key_data()

    def flat(self):
        """ Get the flat data. """
        return self.flat_updated if self.flat_updated else\
            self.flat_image_key_data()


class NoImageKey(Tomo):
    """ This class is used to get data from a dataset with separate darks and
        flats. """

    def __init__(self, data_obj, image_key, proj_dim):
        super(NoImageKey, self).__init__(data_obj, proj_dim, image_key)
        self.dark_path = None
        self.flat_path = None
        self.orig_image_key = copy.copy(image_key)
        self.flat_image_key = False
        self.dark_image_key = False
        if self.image_key is not None:
            self.shape = self._get_image_key_data_shape()
            self._getitem = self._getitem_imagekey
        else:
            self.shape = data_obj.data.shape
            self._getitem = self._getitem_noimagekey
        self.data_obj = data_obj
        self.nDims = len(self.shape)

    def __getitem__(self, idx):
        return self._getitem(idx)

    def _copy(self, new_obj):
        new_obj.dark_path = self.dark_path
        new_obj.flat_path = self.flat_path
        new_obj.flat_image_key = self.flat_image_key
        new_obj.dark_image_key = self.dark_image_key
        self._copy_base(new_obj)

    def _set_flat_path(self, path, imagekey=False):
        self.flat_image_key = imagekey
        self.flat_path = path

    def _set_dark_path(self, path, imagekey=False):
        self.dark_image_key = imagekey
        self.dark_path = path

    def get_shape(self):
        return self.shape

    def dark(self):
        """ Get the dark data. """
        if self.dark_updated:
            return self.dark_updated
        if self.dark_image_key is not False:
            self.image_key = self.dark_image_key
            dark = self.dark_image_key_data()
            self.image_key = self.orig_image_key
            return dark
        return self.dark_path[self.dark_flat_slice_list]*self.dscale

    def flat(self):
        """ Get the flat data. """
        if self.flat_updated:
            return self.flat_updated()
        if self.flat_image_key is not False:
            self.image_key = self.flat_image_key
            flat = self.flat_image_key_data()
            self.image_key = self.orig_image_key
            return flat
        return self.flat_path[self.dark_flat_slice_list]*self.fscale


class MultipleImageKey(DataTypes):
    """ This class is used to combine multiple Data objects containing\
        ImageKey objects. """

    def __init__(self, data_obj_list, stack_or_cat, dim):
        self.obj_list = data_obj_list
        self.stack_or_cat = stack_or_cat
        self.dim = dim
        self.shape = None
        self._set_shape()
        if self.stack_or_cat == 'stack':
            self.inc = 1
        else:
            self.inc = self.obj_list[0].get_shape()[self.dim]

    def __getitem__(self, idx):
        obj_list, in_slice_list, out_slice_list = self._get_lists(idx)
        size = [len(np.arange(s.start, s.stop, s.step)) for s in idx]
        data = np.empty(size)

        for i in range(len(obj_list)):
            data[tuple(out_slice_list[i])] = \
                obj_list[i].data[tuple(in_slice_list[i])]

        return data

    def _get_lists(self, idx):
        inc = self.inc
        entry = idx[self.dim]
        init_vals = np.arange(entry.start, entry.stop, entry.step)
        array = init_vals % inc
        index = np.where(np.diff(array) < 0)[0] + 1
        val_list = np.array_split(array, index)

        # get the relevant Data objects
        obj_vals = init_vals[np.append(0, index)]/inc
        active_obj_list = []
        for i in obj_vals:
            active_obj_list.append(self.obj_list[i])

        # set the input and output slice lists
        in_slice_list = np.tile(idx, (len(val_list), 1))
        new_slices = [slice(e[0], e[-1]+1, entry.step) for e in val_list]
        in_slice_list[:, self.dim] = new_slices

        out_slice_list = self._set_out_slice_list(idx, val_list)

        return active_obj_list, in_slice_list, out_slice_list

    def _set_out_slice_list(self, idx, val_list):
        out_slice_list = \
            [slice(0, len(np.arange(s.start, s.stop, s.step))) for s in idx]
        out_slice_list = np.tile(out_slice_list, (len(val_list), 1))
        length = np.append(0, np.cumsum([len(v) for v in val_list]))

        if self.stack_or_cat == 'cat':
            new_slices = \
                [slice(length[i-1], length[i]) for i in range(1, len(length))]
        else:
            new_slices = [slice(i, i+1) for i in range(len(val_list))]
        out_slice_list[:, self.dim] = new_slices

        return out_slice_list

    def get_shape(self):
        return self.shape

    def _set_shape(self):
        nObjs = len(self.obj_list)
        shape = list(self.obj_list[0].data.shape)
        if self.stack_or_cat == 'cat':
            shape[self.dim] *= nObjs
        else:
            shape.insert(self.dim, nObjs)
        self.shape = tuple(shape)
