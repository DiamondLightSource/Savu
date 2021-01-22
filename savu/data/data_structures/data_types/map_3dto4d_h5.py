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
.. module:: map_3dto4d_h5
   :platform: Unix
   :synopsis: A module for loading a 3D hdf5 dataset that contains a set of \
       4D scans.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.data.data_structures.data_types.base_type import BaseType


class Map3dto4dh5(BaseType):
    """ This class converts a 3D dataset to a 4D dataset. """

    def __init__(self, data_obj, n_angles):
        self.data_obj = data_obj
        self.data = data_obj.data
        self.n_angles = n_angles
        shape = self.data.shape
        super(Map3dto4dh5, self).__init__()

        import inspect
        if inspect.isclass(type(self.data)):
            self.add_base_class_with_instance(type(self.data), self.data)

        new_shape = (n_angles, shape[1], shape[2], shape[0] // n_angles)
        self.shape = new_shape

    def clone_data_args(self, args, kwargs, extras):
        args = ['self', 'n_angles']
        return args, kwargs, extras

    def __getitem__(self, idx):
        rot_dim = \
            self.data_obj.get_data_dimension_by_axis_label('rotation_angle')
        n_angles = self.shape[rot_dim]
        idx_dim3 = np.arange(idx[3].start, idx[3].stop, idx[3].step)
        idx_dim0 = np.arange(idx[0].start, idx[0].stop, idx[0].step)
        idx_dim0 = np.ravel(idx_dim3.reshape(-1, 1)*n_angles + idx_dim0)

        size = [len(np.arange(i.start, i.stop, i.step)) for i in idx]
        data = np.empty(size)

        change = np.where(idx_dim0[:-1] // n_angles != idx_dim0[1:] // n_angles)[0]
        start = idx_dim0[np.append(0, change+1)]
        stop = idx_dim0[np.append(change, len(idx_dim0)-1)] + 1
        length = stop - start

        for i in range(len(start)):
            new_slice = (slice(start[i], stop[i], idx[0].step), idx[1], idx[2])
            data[0:length[i], :, :, i] = self.data[new_slice]
        return data

    def get_shape(self):
        return self.shape
