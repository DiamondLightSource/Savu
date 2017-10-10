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
.. module:: fabio
   :platform: Unix
   :synopsis: A module for loading any of the FabIO python module supported \
       image formats (e.g. tiffs)

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
import fabio
import os

from savu.data.data_structures.data_types.base_type import BaseType


class FabIO(BaseType):
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
        if prefix is not None:
            fullpath = os.path.join(folder, prefix + '*')
        else:
            fullpath += "/*"
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
