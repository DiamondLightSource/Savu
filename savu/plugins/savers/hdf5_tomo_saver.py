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
import copy
from mpi4py import MPI

import numpy as np
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
            backing_file = h5py.File(filename, 'w', driver='mpio',
                                     comm=MPI.COMM_WORLD)
        else:
            backing_file = h5py.File(filename, 'w')

        print "creating the backing file", filename
        if backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        logging.debug("Creating file '%s' '%s'",
                      expInfo.get_meta_data("group_name"),
                      backing_file.filename)

        return backing_file

    def create_entries(self, data, key, current_and_next):
        expInfo = self.exp.meta_data
        group_name = expInfo.get_meta_data(["group_name", key])
        try:
            group_name = group_name + '_' + data.name
        except AttributeError:
            pass

        group = data.backing_file.create_group(group_name)
        group.attrs[NX_CLASS] = 'NXdata'
        group.attrs['signal'] = 'data'

        logging.info("create_entries: 1")
        self.exp.barrier()

        if data.get_variable_flag() is True:
            dt = h5py.special_dtype(vlen=data.dtype)
            data.data = group.create_dataset('data', data.get_shape()[:-1], dt)
        else:
            shape = data.get_shape()
            if current_and_next is 0:
                data.data = group.create_dataset("data", shape,
                                                 data.dtype)
            else:

                logging.info("create_entries: 2")
                self.exp.barrier()

                chunks = self.calculate_chunking(current_and_next, shape,
                                                 data.dtype)
                logging.info("create_entries: 3")
                self.exp.barrier()
                print "chunks = ", chunks
                data.data = group.create_dataset("data", shape, data.dtype,
                                                 chunks=chunks)
                logging.info("create_entries: 4")
                self.exp.barrier()

        return group_name, group

    def calculate_chunking(self, current_and_next, shape, ttype):
        print "shape = ", shape
        if len(shape) < 3:
            return True
        current = current_and_next['current']
        current_cores = current[current.keys()[0]]['core_dir']
        nnext = current_and_next['next']

        #print "current", current, "next", nnext
        if nnext == []:
            next_cores = current_cores
        else:
            next_cores = nnext[nnext.keys()[0]]['core_dir']
        chunks = [1]*len(shape)
        intersect = set(current_cores).intersection(set(next_cores))

        if 'VOLUME' in current.keys()[0]:
            for dim in range(3):
                chunks[dim] = min(shape[dim], 64)
        else:
            for dim in intersect:
                chunks[dim] = shape[dim]
            remaining_cores = set(current_cores).difference(intersect).\
                union(set(next_cores).difference(intersect))
            for dim in remaining_cores:
                chunks[dim] = min(shape[dim], 8)  # change 8 to max_shape?

        if 0 in chunks:
            return True
        else:
            return self.adjust_chunk_size(chunks, ttype, shape)

    def adjust_chunk_size(self, chunks, ttype, shape):
        chunks = np.array(chunks)
        chunk_size = np.prod(chunks)*np.dtype(ttype).itemsize
        cache_size = 1000000
        if (chunk_size > cache_size):
            while ((np.prod(chunks)*np.dtype(ttype).itemsize) > 1000000):
                idx = np.argmax(chunks)
                chunks[idx] = chunks[idx]-1
        else:
            next_chunks = chunks
            while (((np.prod(next_chunks)*np.dtype(ttype).itemsize) < 1000000)
                    and not np.array_equal(chunks, np.array(shape))):
                chunks = copy.copy(next_chunks)
                idx = self.get_idx(next_chunks, shape)
                next_chunks[idx] = next_chunks[idx]+1
        return tuple(chunks)

    def get_idx(self, chunks, shape):
        idx_order = np.argsort(chunks)
        i = 0
        for i in range(len(shape)):
            if (chunks[idx_order[i]] < shape[idx_order[i]]):
                break

        return idx_order[i]
