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

    def __init__(self, folder, Data, dim):
        self._data_obj = Data
        self.nFrames = None
        self.start_file = fabio.open(self.__get_file_name(folder))
        self.frame_dim = dim

    def __getitem__(self, index):
        idx = index[self.frame_dim]
        frame_list = np.arange(idx.start, idx.stop, idx.step)

        size = []
        for i in index:
            size.append(len(np.arange(i.start, i.stop, i.step)))

        data = np.empty(size)
        tiffidx = [i for i in range(len(index)) if i is not self.frame_dim]
        index = list(index)

        dataidx = 0
        for i in frame_list:
            index[self.frame_dim] = slice(dataidx, dataidx+1, idx.step)
            data[index] = \
                self.start_file.getframe(i).data[[index[i] for i in tiffidx]]
            dataidx += 1
        return data

    def __get_file_name(self, folder):
        files = os.listdir(folder)
        self.nFrames = len(files)
        fname = files[0]
        return folder + "/" + fname

    def get_shape(self):
        return (self.nFrames, self.start_file.dim2, self.start_file.dim1)
