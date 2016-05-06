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

    def __init__(self, folder, Data, dim, shape=None):
        self._data_obj = Data
        self.nFrames = None
        self.start_file = fabio.open(self.__get_file_name(folder))
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
        index, frameidx = self.__get_indices(index, size)

        for i in range(len(frameidx)):
            data[index[i]] = \
                self.start_file.getframe(self.start_no + frameidx[i])\
                .data[[index[i][n] for n in tiffidx]]
        return data

    def __get_file_name(self, folder):
        import re
        files = os.listdir(folder)
        self.nFrames = len(files)
        fname = sorted(files)[0]
        self.start_no = [int(s) for s in re.findall(r'\d+', fname)][-1]
        return folder + "/" + fname

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


class Map_3d_to_4d_h5(DataTypes):
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
