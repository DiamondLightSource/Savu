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
.. module:: mrc
   :platform: Unix
   :synopsis: A module to load MRC image data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from savu.data.data_structures.data_types.base_type import BaseType
import mrcfile
import numpy as np


class MRC(BaseType):

    def __init__(self, Data, filename, stats=None):
        self._data_obj = Data
        self.filename = filename
        super(MRC, self).__init__()
        self.file = mrcfile.mmap(filename, 'r')
        self.dtype = self.file.data.dtype

    def __getitem__(self, idx):
        data = self.file.data[idx].astype(np.float32)
        data /= 65535.0
        return data

    def get_shape(self):
        return self.file.data.shape

    def clone_data_args(self, args, kwargs, extras):
        args = ['self', 'filename']
        kwargs['stats'] = 'stats'
        return args, kwargs, extras

    def close(self):
        self.file.close()
