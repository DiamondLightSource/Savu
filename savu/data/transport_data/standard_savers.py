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
.. module:: standard_loaders
   :platform: Unix
   :synopsis: Classes for different experimental setups containing standard
   data loaders.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import h5py
import logging

from mpi4py import MPI

NX_CLASS = 'NX_class'


class TomographySavers(object):
    """
    This class is called from a tomography loader when using a standard saver.
    It deals with saving of the data to different standard formats
    """

    def __init__(self, exp, params):
        self.saver_setup(exp)
        self.parameters = params

    def saver_setup(self, exp):
        pass

    def save_to_hdf5(self, exp):
        for key in exp.index["out_data"].keys():
            out_data = exp.index["out_data"][key]
            out_data.backing_file = self.create_backing_h5(key, exp.meta_data)
            out_data.group_name, out_data.group = \
                self.create_entries(out_data, exp.meta_data, key)

    def create_backing_h5(self, key, expInfo):
        """
        Create a h5 backend for output data
        """
        filename = expInfo.get_meta_data(["filename", key])
        if expInfo.get_meta_data("mpi") is True:
            backing_file = h5py.File(filename, 'w', driver='mpio',
                                     comm=MPI.COMM_WORLD)
        else:
            backing_file = h5py.File(filename, 'w')

        print "creating file", filename
        if backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        logging.debug("Creating file '%s' '%s'",
                      expInfo.get_meta_data("group_name"),
                      backing_file.filename)

        return backing_file

    def create_entries(self, data, expInfo, key):

        group_name = expInfo.get_meta_data(["group_name", key])
        try:
            group_name = group_name + '_' + data.name
        except AttributeError:
            pass
        group = data.backing_file.create_group(group_name)
        group.attrs[NX_CLASS] = 'NXdata'
        group.attrs['signal'] = 'data'

        if data.get_variable_flag() is True:
            dtype = h5py.special_dtype(vlen=data.dtype)
        else:
            dtype = data.dtype

        data.data = group.create_dataset('data', data.get_shape(), dtype)
        return group_name, group
