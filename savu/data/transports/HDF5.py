# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: HDF5
   :platform: Unix
   :synopsis: Transport for saving and loading files using hdf5

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import h5py

from savu.data.structures import NX_CLASS
from savu.data.TransportMechanism import TransportMechanism


# TODO tidy up the NeXus format parts of this
class HDF5(TransportMechanism):

    def setup(self, path, name):
        self.backing_file = h5py.File(path, 'w')
        if self.backing_file is None:
            raise IOError("Failed to open the hdf5 file")
        self.group = self.backing_file.create_group(name)
        self.group.attrs[NX_CLASS] = 'NXdata'

    def add_data_block(self, name, shape, dtype):
        self.group.create_dataset(name, shape, dtype)

    def get_data_block(self, name):
        return self.group[name]

    def finalise(self):
        if self.backing_file is not None:
            self.backing_file.close()
            self.backing_file = None
