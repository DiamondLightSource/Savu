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
.. module:: image_data
   :platform: Unix
   :synopsis: A module for loading any of the FabIO python module supported \
       image formats (e.g. tiffs)

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import fabio
import numpy as np

from savu.data.data_structures.data_types.base_type import BaseType


class ImageData(BaseType):
    """ This class loads any of the FabIO python module
    supported image formats. """

    def __init__(self, folder, Data, dim, shape=None, data_prefix=None):
        self.folder = folder
        self._data_obj = Data
        self.frame_dim = dim
        self.shape = shape
        self.prefix = data_prefix
        super(ImageData, self).__init__()

        self.nFrames = None

        self.file_names = self.__get_file_names(folder, data_prefix)
        self.start_file = fabio.open(self.file_names[0])
        self.dtype = self.start_file.data[0, 0].dtype
        self.image_shape = (self.start_file.dim2, self.start_file.dim1)

        if shape is None:
            self.shape = (self.nFrames,)
        else:
            self.shape = shape

        self.full_shape = self.image_shape + self.shape
        self.image_dims = set(np.arange(len(self.full_shape)))\
            .difference(set(self.frame_dim))

    def clone_data_args(self, args, kwargs, extras):
        args = ['folder', 'self', 'frame_dim']
        kwargs['shape'] = 'shape'
        kwargs['prefix'] = 'prefix'
        return args, kwargs, extras

    def __getitem__(self, index):
        index = [index[i] if index[i].start is not None else
                 slice(0, self.shape[i]) for i in range(len(index))]
        size = [len(np.arange(i.start, i.stop, i.step)) for i in index]
        data = np.empty(size, dtype=self.dtype)
        tiff_slices = [index[i] for i in self.image_dims]

        # shift tiff dims to start from 0
        index = list(index)
        for i in self.image_dims:
            end = \
                len(np.arange(0, index[i].stop-index[i].start, index[i].step))
            index[i] = slice(0, end, 1)

        index, frameidx = self.__get_indices(index, size)

        for i in range(len(frameidx)):
            image = fabio.open(self.file_names[frameidx[i]]).data[tuple(tiff_slices)]
            for d in self.frame_dim:
                image = np.expand_dims(image, axis=d)
            data[tuple(index[i])] = image

        return data

    def __get_file_names(self, folder, prefix):
        import re
        import glob
#        files = os.listdir(folder)
        fullpath = str.strip(folder)
        if prefix is not None:
            fullpath = os.path.join(folder, prefix + '*')
        else:
            fullpath = os.path.join(fullpath, '*')
        files = glob.glob(fullpath)
        self.nFrames = len(files)
        file_nos = [int(re.findall(r'\d+', f)[-1]) for f in files]
        sort_idx = np.argsort(file_nos)
        self.start_no = file_nos[sort_idx[0]]
        return list(np.array(files)[sort_idx])

    def get_shape(self):
        dims = list(self.image_dims) + self.frame_dim
        shape = [x for _, x in sorted(zip(dims, self.full_shape))]
        return tuple(shape)

    def __get_idx(self, dim, sl, shape):
        c = int(np.prod(shape[0:dim]))
        r = int(np.prod(shape[dim+1:]))
        vals = np.arange(sl.start, sl.stop, sl.step)
        vals_shift = np.arange(0, len(vals), 1)
        return [np.ravel(np.kron(v, np.ones((r, c)))) for v in \
                [vals, vals_shift]]

    def __get_indices(self, index, size):
        """ Get the indices for the new data array and the file numbers. """
        # indices for non-image dims only
        sub_idx = np.array(index)[np.array(self.frame_dim)]
        sub_size = [size[i] for i in self.frame_dim]

        idx_list = []
        frame_list = []
        for dim in range(len(sub_idx)):
            frame, idx = self.__get_idx(dim, sub_idx[dim], sub_size)
            frame_list.append(frame.astype(int))
            idx_list.append(idx.astype(int))

        lshape = idx_list[0].shape[0]  # this is just size of first frame dim? sub_size[0]
        index = np.tile(index, (lshape, 1))
        frameidx = np.zeros(lshape)

        for dim in range(len(sub_idx)):
            index[:, self.frame_dim[dim]] = \
                [slice(i, i+1, 1) for i in idx_list[dim]]
            frameidx[:] += frame_list[dim]*np.prod(self.shape[dim+1:])
        return index.tolist(), frameidx.astype(int)
