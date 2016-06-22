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


class DataTypes(object):

    def __getitem__(self, index):
        """ Override __getitem__ and map to the relevant files """
        raise NotImplementedError("__getitem__ must be implemented.")

    def get_shape(self):
        """ Get full stiched shape of a stack of files"""
        raise NotImplementedError("get_shape must be implemented.")


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


class ImageKey(DataTypes):
    """ This class is used to get data from a dataset with an image key. """

    def __init__(self, data_obj, image_key, proj_dim):
        self.data = data_obj.data
        self.image_key = image_key
        self.proj_dim = proj_dim

        data_idx = self.get_index(0)
        new_shape = list(self.data.shape)
        new_shape[proj_dim] = len(data_idx)
        self.shape = tuple(new_shape)
        self.nDims = len(self.shape)
        data_obj.meta_data.set('dark', self.dark_mean())
        data_obj.meta_data.set('flat', self.flat_mean())

    def __getitem__(self, idx):
        index = list(idx)
        index[self.proj_dim] = self.get_index(0)[idx[self.proj_dim]].tolist()
        return self.data[tuple(index)]

    def get_shape(self):
        return self.shape

    def get_image_key(self):
        return self.image_key

    def get_index(self, key):
        """ Get the projection index of a specific image key value.

        :params int key: the image key value
        """
        return np.where(self.image_key == key)[0]

    def __get_data(self, key):
        index = [slice(None)]*self.nDims
        index[self.proj_dim] = self.get_index(key)
        return self.data[tuple(index)]

    def dark(self):
        """ Get the dark data. """
        return self.__get_data(2)

    def flat(self):
        """ Get the flat data. """
        return self.__get_data(1)

    def dark_mean(self):
        """ Get the averaged dark projection data. """
        return self.__get_data(2).mean(self.proj_dim).astype(np.float32)

    def flat_mean(self):
        """ Get the averaged flat projection data. """
        return self.__get_data(1).mean(self.proj_dim).astype(np.float32)
