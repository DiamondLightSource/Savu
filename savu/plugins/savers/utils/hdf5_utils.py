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

import h5py
import logging
from mpi4py import MPI

from savu.data.chunking import Chunking
from savu.data.data_structures.data_types.data_plus_darks_and_flats \
    import NoImageKey

NX_CLASS = 'NX_class'


class Hdf5Utils(object):
    """
    A class to save tomography data to a hdf5 file
    """

    def __init__(self, exp):
        self.plugin = None
        self.info = MPI.Info.Create()
        self.exp = exp
        self.info.Set("romio_ds_write", "disable")  # this setting is required
        self.info.Set("romio_ds_read", "disable")
        # info.Set("romio_cb_read", "disable")
        # info.Set("romio_cb_write", "disable")

    def _open_backing_h5(self, filename, mode):
        """
        Create a h5 backend for output data
        """
        self.exp._barrier()

        if self.exp.meta_data.get("mpi") is True:
            backing_file = h5py.File(filename, mode, driver='mpio',
                                     comm=MPI.COMM_WORLD, info=self.info)
        else:
            backing_file = h5py.File(filename, mode)

        self.exp._barrier()

        if backing_file is None:
            raise IOError("Failed to open the hdf5 file")
        return backing_file

    def _link_datafile_to_nexus_file(self, data):
        filename = self.exp.meta_data.get('nxs_filename')

        with h5py.File(filename, 'a') as nxs_file:
            # entry path in nexus file
            name = data.get_name()
            group_name = self.exp.meta_data.get(['group_name', name])
            link_type = self.exp.meta_data.get(['link_type', name])
            nxs_entry = '/entry/' + link_type
            if link_type == 'final_result':
                nxs_entry += '_' + data.get_name()
            else:
                nxs_entry += "/" + group_name
            nxs_entry = nxs_file[nxs_entry]
            nxs_entry.attrs['signal'] = 'data'
            data_entry = nxs_entry.name + '/data'
            # output file path
            h5file = data.backing_file.filename

            # entry path in output file path
            m_data = self.exp.meta_data.get
            if not (link_type == 'intermediate' and
                    m_data('inter_path') != m_data('out_path')):
                h5file = h5file.split(m_data('out_folder') + '/')[-1]

            nxs_file[data_entry] = \
                h5py.ExternalLink(h5file, group_name + '/data')

    def __create_dataset_nofill(self, group, name, shape, dtype, chunks=None):
        spaceid = h5py.h5s.create_simple(shape)
        plist = h5py.h5p.create(h5py.h5p.DATASET_CREATE)
        plist.set_fill_time(h5py.h5d.FILL_TIME_NEVER)
        if chunks not in [None, []] and isinstance(chunks, tuple):
            plist.set_chunk(chunks)
        typeid = h5py.h5t.py_create(dtype)
        datasetid = h5py.h5d.create(
                group.file.id, group.name+'/'+name, typeid, spaceid, plist)
        data = h5py.Dataset(datasetid)
        return data

    def _create_entries(self, data, key, current_and_next):
        self.exp._barrier()

        expInfo = self.exp.meta_data
        group_name = expInfo.get(["group_name", key])
        data.data_info.set('group_name', group_name)
        try:
            group_name = group_name + '_' + data.name
        except AttributeError:
            pass

        self.exp._barrier()
        group = data.backing_file.create_group(group_name)
        self.exp._barrier()
        shape = data.get_shape()
        if current_and_next is 0:
            logging.warn('Creating the dataset without chunks')
            data.data = group.create_dataset("data", shape, data.dtype)
        else:

            # change cache properties
            propfaid = group.file.id.get_access_plist()
            settings = list(propfaid.get_cache())
            settings[2] *= 1
            propfaid.set_cache(*settings)
            # calculate total number of chunks and set nSlots=nChunks

            chunking = Chunking(self.exp, current_and_next)
            chunks = chunking._calculate_chunking(shape, data.dtype,
                                                  chunk_max=settings[2])

            self.exp._barrier()
            data.data = self.__create_dataset_nofill(
                group, "data", shape, data.dtype, chunks=chunks)

        self.exp._barrier()

        return group_name, group

    def _close_file(self, data):
        """
        Closes the backing file
        """
        self.exp._barrier()
        logging.debug("Attempting to close the file ")

        if data.backing_file is not None:
            try:
                filename = data.backing_file.filename
                data.backing_file.close()
                logging.debug("File close successful: %s", filename)
                data.backing_file = None
            except:
                logging.debug("File close unsuccessful", filename)
        self.exp._barrier()

    def _reopen_file(self, data, mode):
        filename = data.backing_file.filename
        self._close_file(data)
        logging.debug(
                "Re-opening the backing file %s in mode %s" % (filename, mode))
        data.backing_file = self._open_backing_h5(filename, mode)
        entry = data.backing_file.keys()[0] + '/data'

        if isinstance(data.data, NoImageKey):
            data.data.data = data.backing_file[entry]
        elif isinstance(data.data, h5py._hl.dataset.Dataset):
            data.data = data.backing_file[entry]
        else:
            raise Exception('Unable to re-open the hdf5 file - unknown'
                            ' datatype')
