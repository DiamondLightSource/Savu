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
   :synopsis: A class to create hdf5 output files

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


import h5py
import logging
from mpi4py import MPI

from savu.plugins.base_saver import BaseSaver
from savu.plugins.utils import register_plugin
from savu.data.chunking import Chunking

NX_CLASS = 'NX_class'


@register_plugin
class Hdf5TomoSaver(BaseSaver):
    """
    A class to save tomography data to a hdf5 file
    """

    def __init__(self, name='Hdf5TomoSaver'):
        super(Hdf5TomoSaver, self).__init__(name)
        self.plugin = None

    def setup(self):
        exp = self.exp
        out_data_dict = exp.index["out_data"]
        current_and_next = [0]*len(out_data_dict)
        if 'current_and_next' in self.exp.meta_data.get_dictionary():
            current_and_next = \
                self.exp.meta_data.get_meta_data('current_and_next')

        logging.info("saver setup: 1")
        exp.barrier()

        count = 0
        for key in out_data_dict.keys():
            out_data = out_data_dict[key]

            logging.info("saver setup: 2")
            self.exp.barrier()
            out_data.backing_file = self.create_backing_h5(key)

            logging.info("saver setup: 3")
            self.exp.barrier()

            out_data.group_name, out_data.group = \
                self.create_entries(out_data, key, current_and_next[count])

            logging.info("saver setup: 4")
            self.exp.barrier()

            count += 1

    def create_backing_h5(self, key):
        """
        Create a h5 backend for output data
        """
        expInfo = self.exp.meta_data

        filename = expInfo.get_meta_data(["filename", key])
        if expInfo.get_meta_data("mpi") is True:

            info = MPI.Info.Create()
            info.Set("romio_ds_read", "disable")
            info.Set("romio_ds_write", "disable")
#            info.Set("romio_cb_read", "enable")
#            info.Set("romio_cb_write", "disable")
            backing_file = h5py.File(filename, 'w', driver='mpio',
                                     comm=MPI.COMM_WORLD, info=info)
            # fapl = backing_file.id.get_access_plist()
            # comm, info = fapl.get_fapl_mpio()
        else:
            backing_file = h5py.File(filename, 'w')

        logging.debug("creating the backing file %s", filename)
        if backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        logging.debug("Creating file '%s' '%s'",
                      expInfo.get_meta_data("group_name"),
                      backing_file.filename)

        return backing_file

    def create_entries(self, data, key, current_and_next):
        expInfo = self.exp.meta_data
        group_name = expInfo.get_meta_data(["group_name", key])
        data.data_info.set_meta_data('group_name', group_name)
        try:
            group_name = group_name + '_' + data.name
        except AttributeError:
            pass

        group = data.backing_file.create_group(group_name)
        group.attrs[NX_CLASS] = 'NXdata'
        group.attrs['signal'] = 'data'

        logging.info("create_entries: 1")
        self.exp.barrier()

        shape = data.get_shape()
        if current_and_next is 0:
            data.data = group.create_dataset("data", shape, data.dtype)
        else:
            logging.info("create_entries: 2")
            self.exp.barrier()

            chunking = Chunking(self.exp, current_and_next)
            chunks = chunking.calculate_chunking(shape, data.dtype)
            logging.info("create_entries: 3")
            self.exp.barrier()
            data.data = group.create_dataset("data", shape, data.dtype,
                                             chunks=chunks)
            logging.info("create_entries: 4")
            self.exp.barrier()

        return group_name, group
