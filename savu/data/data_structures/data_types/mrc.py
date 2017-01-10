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
.. module:: base_type
   :platform: Unix
   :synopsis: A module to load MRC image data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

import savu.plugins.loaders.utils.mrc_header as header_format


class MRC(object):

    def __init__(self, Data, filename, stats=None):
        self._data_obj = Data
        self.yz_swapped = False
        header_size = 1024
        self.file = open(filename, 'rb')
        # get the header information and file pointer position of first data
        # entry
        header, first = self.__get_header(self.file, header_size)
        self.header_dict = self.__get_header_dict(header)
        self.format = self.__set_data_format(header)
        self.shape = self.__set_shape(header)
        if self.format['mode'] == 16:
            self.shape = self.shape + (3,)

        self.data = np.memmap(filename, dtype=self.format['dtype'], mode='r',
                              offset=first, shape=self.shape)

    def __getitem__(self, idx):
        return self.data[idx]

    def __get_header(self, fd, size):
        rec_header_dtype = np.dtype(header_format.rec_header_dtd)
        assert rec_header_dtype.itemsize == size
        header = np.fromfile(fd, dtype=header_format.rec_header_dtd, count=1)
        # Seek header
        if header['next'] > 0:
            fd.seek(header['next'])  # ignore extended header
        return header, fd.tell()

    def __get_header_dict(self, header):
        header_dict = {}
        for name in header.dtype.names:
            header_dict[name] = header[name][0] if len(header[name]) == 1 \
                                else header[name]
        return header_dict

    def __set_data_format(self, header):
        mode = header['mode']
        # BitOrder: little or big endian
        bo = "<" if header['stamp'][0, 0] == 68 and \
             header['stamp'][0, 1] == 65 else "<"
        sign = "i1" if header['imodFlags'] == 1 else "u1"  # signed or unsigned
        dtype = [sign, "i2", "f",  "c4", "c8", None, "u2", None, None, None,
                 None, None, None, None, None, None, "u1"][mode]
        dsize = [1, 2, 4, 4, 8, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3][mode]
        return {'mode': mode, 'bo': bo, 'sign': sign, 'dtype': bo+dtype,
                'dsize': dsize}

    def __set_shape(self, header):
        nx, ny, nz = header['nx'], header['ny'], header['nz']
        if not isinstance(nx, int):
            nx = nz[0]
            ny = ny[0]
            nz = nz[0]
        return (nx, ny, nz)

    def get_shape(self):
        return self.shape
