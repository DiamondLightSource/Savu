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
.. module:: hdf5_utils
   :platform: Unix
   :synopsis: A class containing savu specific hdf5 functions.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import h5py
import logging
from mpi4py import MPI

from savu.data.chunking import Chunking
#from savu.data.data_structures.data_types.data_plus_darks_and_flats \
#    import NoImageKey
from savu.data.data_structures.data_types.base_type import BaseType
from savu.core.iterate_plugin_group_utils import \
    check_if_end_plugin_in_iterate_group


NX_CLASS = 'NX_class'


class Hdf5Utils(object):
    """
    A class to save tomography data to a hdf5 file
    """

    def __init__(self, exp):
        self.plugin = None
        self.info = MPI.Info.Create()
        self.exp = exp
        # Get MPI I/O settings from the Savu config file
        settings = self.exp.meta_data.get(['system_params', 'mpi-io_settings'])
        for key, value in settings.items():
            self.info.Set(key, value)

    def _open_backing_h5(self, filename, mode, comm=MPI.COMM_WORLD, mpi=True):
        """
        Create a h5 backend for output data
        """
        if mpi:
            msg = self.__class__.__name__ + "_open_backing_h5 %s" + filename
            self.exp._barrier(communicator=comm, msg=msg+'1')

        kwargs = {'driver': 'mpio', 'comm': comm, 'info': self.info}\
            if self.exp.meta_data.get('mpi') and mpi else {}

        backing_file = h5py.File(filename, mode, **kwargs)

        if mpi:
            self.exp._barrier(communicator=comm, msg=msg+'2')

        if backing_file is None:
            raise IOError("Failed to open the hdf5 file")
        return backing_file

    def _link_datafile_to_nexus_file(self, data):
        filename = self.exp.meta_data.get('nxs_filename')

        with h5py.File(filename, 'a') as nxs_file:
            # entry path in nexus file
            name = data.get_name()
            group_name = self.exp.meta_data.get(['group_name', name])
            link = self.exp.meta_data.get(['link_type', name])
            if check_if_end_plugin_in_iterate_group(self.exp):
                # TODO: for now, for iterative groups of plugins, allow the
                # cloned dataset to be linked in the output NeXuS file (by
                # letting its "clone name" be the value of the name variable,
                # rather than the name of the original dataset that it was
                # cloned from)
                name = data.get_name(orig=False)
            else:
                name = data.get_name(orig=True)
            nxs_entry = self.__add_nxs_entry(nxs_file, link, group_name, name)
            self.__add_nxs_data(nxs_file, nxs_entry, link, group_name, data)

    def __add_nxs_entry(self, nxs_file, link, group_name, name):
        nxs_entry = '/entry/' + link
        nxs_entry += '_' + name if link == 'final_result' else "/" + group_name
        nxs_entry = nxs_file[nxs_entry]
        nxs_entry.attrs['signal'] = 'data'
        return nxs_entry

    def __add_nxs_data(self, nxs_file, nxs_entry, link, group_name, data):
        data_entry = nxs_entry.name + '/data'
        # output file path
        h5file = data.backing_file.filename

        if link == 'input_data':
            dataset = self.__is_h5dataset(data)
            if dataset:
                nxs_file[data_entry] = \
                    h5py.ExternalLink(os.path.abspath(h5file), dataset.name)
        else:
            # entry path in output file path
            m_data = self.exp.meta_data.get
            if not (link == 'intermediate' and
                    m_data('inter_path') != m_data('out_path')):
                h5file = h5file.split(m_data('out_folder') + '/')[-1]
            nxs_file[data_entry] = \
                h5py.ExternalLink(h5file, group_name + '/data')

    def __is_h5dataset(self, data):
        if isinstance(data.data, h5py.Dataset):
            return data.data
        try:
            if isinstance(data.data.data, h5py.Dataset):
                return data.data.data
        except:
            return False

    def create_dataset_nofill(self, group, name:str, shape, dtype, chunks=None):
        spaceid = h5py.h5s.create_simple(shape)
        plist = h5py.h5p.create(h5py.h5p.DATASET_CREATE)
        plist.set_fill_time(h5py.h5d.FILL_TIME_NEVER)
        if chunks not in [None, []] and isinstance(chunks, tuple):
            plist.set_chunk(chunks)
        typeid = h5py.h5t.py_create(dtype)
        group_name = (group.name + '/' + name).encode("ascii")
        datasetid = h5py.h5d.create(
            group.file.id, group_name, typeid, spaceid, plist)
        data = h5py.Dataset(datasetid)
        return data

    def _create_entries(self, data, key:str, current_and_next):
        msg = self.__class__.__name__ + '_create_entries'
        self.exp._barrier(msg=msg+'1')

        expInfo = self.exp.meta_data
        group_name = expInfo.get(["group_name", key])
        data.data_info.set('group_name', group_name)
        try:
            group_name = group_name + '_' + data.name
        except AttributeError:
            pass

        self.exp._barrier(msg=msg+'2')
        group = data.backing_file.require_group(group_name)
        self.exp._barrier(msg=msg+'3')
        shape = data.get_shape()

        if 'data' in group:
            data.data = group['data']
        elif current_and_next == 0:
            logging.warning('Creating the dataset without chunks')
            data.data = group.create_dataset("data", shape, data.dtype)
        else:
            chunk_max = self.__set_optimal_hdf5_chunk_cache_size(data, group)
            chunking = Chunking(self.exp, current_and_next)
            chunks = chunking._calculate_chunking(shape, data.dtype,
                                                  chunk_max=chunk_max)

            self.exp._barrier(msg=msg+'4')
            data.data = self.create_dataset_nofill(
                    group, "data", shape, data.dtype, chunks=chunks)

        self.exp._barrier(msg=msg+'5')
        return group_name, group

    def __set_optimal_hdf5_chunk_cache_size(self, data, group):
        # calculate the number first
        # change cache properties
        propfaid = group.file.id.get_access_plist()
        settings = list(propfaid.get_cache())
        pdict = self.exp.meta_data.get('system_params')
        max_chunk_size = pdict['max_chunk_size']
        chunk_cache_size = pdict['chunk_cache_size']
        settings[2] *= chunk_cache_size
        propfaid.set_cache(*settings)
        return max_chunk_size * 1e6  # convert MB to bytes

    def _close_file(self, data):
        """
        Closes the backing file
        """
        if data.backing_file is not None:
            try:
                msg = self.__class__.__name__ + "_close_file" + \
                data.backing_file.filename
                self.exp._barrier(msg=msg)
                logging.debug("Attempting to close the file ")
                filename = data.backing_file.filename
                data.backing_file.close()
                logging.debug("File close successful: %s", filename)
                data.backing_file = None
                data.filename = filename # needed for tests
                self.exp._barrier(msg=msg)
            except:
                logging.debug("File close unsuccessful", filename)

    def _reopen_file(self, data, mode):
        filename = data.backing_file.filename
        self._close_file(data)
        logging.debug(
                "Re-opening the backing file %s in mode %s" % (filename, mode))
        data.backing_file = self._open_backing_h5(filename, mode)
        entry = list(data.backing_file.keys())[0] + '/data'

        if isinstance(data.data, BaseType):
            data.data.data = data.backing_file[entry]
        elif isinstance(data.data, h5py._hl.dataset.Dataset):
            data.data = data.backing_file[entry]
        else:
            raise Exception('Unable to re-open the hdf5 file - unknown'
                            ' datatype')
