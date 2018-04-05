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
.. module:: replicate
   :platform: Unix
   :synopsis: A class to replicate the slice list of a dataset \
       (not the data itself!)

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
import copy

from savu.data.data_structures.data_types.base_type import BaseType


class Replicate(BaseType):
    """ Class to replicate the slice list of a dataset (not the data itself!)
    """

    def __init__(self, data_obj, reps):
        self.data_obj = data_obj
        self.reps = reps
        super(Replicate, self).__init__()

        self.rep_dim = len(data_obj.get_shape()) + 1
        self.shape = data_obj.get_shape() + (reps,)
        self.data = data_obj.data
        self.original_patterns = data_obj.get_data_patterns()
        self.__set_patterns(copy.deepcopy(self.original_patterns))

    def map_input_args(self, args, kwargs, cls, extras):
        args = ['self', 'reps']
        return args, kwargs, cls, extras

    def __getitem__(self, idx):
        return np.expand_dims(self.data[idx[:-1]], self.rep_dim)

    def get_shape(self):
        return self.shape

    def __set_patterns(self, data_obj, patterns):
        for p in patterns:
            patterns[p]['slice_dir'] += (3,)
        data_obj.data_info.set('data_patterns', patterns)

    def _reset(self):
        self.data_obj.data_info.set('data_patterns', self.original_patterns)
        return self.data
