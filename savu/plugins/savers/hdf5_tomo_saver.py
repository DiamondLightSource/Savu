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
.. module:: hdf5_tomo_saver
   :platform: Unix
   :synopsis: A class for saving tomography data using the standard savers
   library.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


import h5py
import logging
from mpi4py import MPI

from savu.core.utils import logmethod
from savu.plugins.base_saver import BaseSaver

from savu.plugins.utils import register_plugin

NX_CLASS = 'NX_class'


@register_plugin
class Hdf5TomoSaver(BaseSaver):
    """
    A class to save tomography data to a hdf5 file
    """

    def __init__(self, name='Hdf5TomoSaver'):
        super(Hdf5TomoSaver, self).__init__(name)

    def setup(self):
        exp = self.exp
        for key in exp.index["out_data"].keys():
            out_data = exp.index["out_data"][key]
            out_data.backing_file = self.create_backing_h5(key)
            out_data.group_name, out_data.group = \
                self.create_entries(out_data, key)

    def create_backing_h5(self, key):
        """
        Create a h5 backend for output data
        """
        expInfo = self.exp.meta_data
        filename = expInfo.get_meta_data(["filename", key])
        if expInfo.get_meta_data("mpi") is True:
            backing_file = h5py.File(filename, 'w', driver='mpio',
                                     comm=MPI.COMM_WORLD)
        else:
            backing_file = h5py.File(filename, 'w')

        if backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        logging.debug("Creating file '%s' '%s'",
                      expInfo.get_meta_data("group_name"),
                      backing_file.filename)

        return backing_file

    def create_entries(self, data, key):
        expInfo = self.exp.meta_data
        group_name = expInfo.get_meta_data(["group_name", key])
        try:
            group_name = group_name + '_' + data.name
        except AttributeError:
            pass

        group = data.backing_file.create_group(group_name)
        group.attrs[NX_CLASS] = 'NXdata'
        group.attrs['signal'] = 'data'

        if data.get_variable_flag() is True:
            dt = h5py.special_dtype(vlen=data.dtype)
            data.data = group.create_dataset('data', data.get_shape()[:-1], dt)
        else:
#            data.data = group.create_dataset('data', data.get_shape(),
#                                             data.dtype)
            logging.debug("*******ADDING CHUNKS TO THE DATA*************")
            data.data = group.create_dataset("data", data.get_shape(),
                                             data.dtype, chunks=True)
        return group_name, group
