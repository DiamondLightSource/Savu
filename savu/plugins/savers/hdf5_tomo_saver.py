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
import numpy as np
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
                self.exp.meta_data.get('current_and_next')

        exp._barrier()

        count = 0
        for key in out_data_dict.keys():
            print key
            out_data = out_data_dict[key]
            self.exp._barrier()
            filename = self.exp.meta_data.get(["filename", key])
            out_data.backing_file = self.__open_backing_h5(filename, 'w')
            self.exp._barrier()
            out_data.group_name, out_data.group = \
                self.__create_entries(out_data, key, current_and_next[count])
            self.exp._barrier()
            count += 1

    def __open_backing_h5(self, filename, mode):
        """
        Create a h5 backend for output data
        """
        if self.exp.meta_data.get("mpi") is True:

            info = MPI.Info.Create()
            info.Set("romio_ds_read", "disable")
            info.Set("romio_ds_write", "disable")
#            info.Set("romio_cb_read", "enable")
#            info.Set("romio_cb_write", "disable")

            backing_file = h5py.File(filename, mode, driver='mpio',
                                     comm=MPI.COMM_WORLD, info=info)
            # fapl = backing_file.id.get_access_plist()
            # comm, info = fapl.get_fapl_mpio()
        else:
            backing_file = h5py.File(filename, mode)

        logging.debug("creating the backing file %s", filename)
        if backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        logging.debug("Creating file '%s' '%s'",
                      self.exp.meta_data.get("group_name"),
                      backing_file.filename)

        return backing_file

    def __create_entries(self, data, key, current_and_next):
        expInfo = self.exp.meta_data
        group_name = expInfo.get(["group_name", key])
        data.data_info.set('group_name', group_name)
        try:
            group_name = group_name + '_' + data.name
        except AttributeError:
            pass

        group = data.backing_file.create_group(group_name)
        group.attrs[NX_CLASS] = 'NXdata'
        group.attrs['signal'] = 'data'

        self.exp._barrier()

        shape = data.get_shape()
        if current_and_next is 0:
            data.data = group.create_dataset("data", shape, data.dtype)
        else:
            self.exp._barrier()
            chunking = Chunking(self.exp, current_and_next)
            chunks = chunking._calculate_chunking(shape, data.dtype)
            self.exp._barrier()
            data.data = group.create_dataset("data", shape, data.dtype,
                                             chunks=chunks)
            self.exp._barrier()

        return group_name, group

    def __output_metadata(self, data, entry):
        self.__output_axis_labels(data, entry)
        self.__output_data_patterns(data, entry)
        self.__output_metadata_dict(data, entry)

    def __output_axis_labels(self, data, entry):
        axis_labels = data.data_info.get("axis_labels")
        axes = []
        count = 0
        for labels in axis_labels:
            name = labels.keys()[0]
            axes.append(name)
            entry.attrs[name + '_indices'] = count

            try:
                mData = data.meta_data.get(name)
                print "outputting the axis label", name
            except KeyError:
                mData = np.arange(data.get_shape()[count])

            if isinstance(mData, list):
                mData = np.array(mData)

            temp = data.group.create_dataset(name, mData.shape, mData.dtype)
            temp[...] = mData[...]
            temp.attrs['units'] = labels.values()[0]
            count += 1
        entry.attrs['axes'] = axes

    def __output_data_patterns(self, data, entry):
        data_patterns = data.data_info.get("data_patterns")
        entry = entry.create_group('patterns')
        entry.attrs['NX_class'] = 'NXcollection'
        for pattern in data_patterns:
            nx_data = entry.create_group(pattern)
            nx_data.attrs[NX_CLASS] = 'NXparameters'
            values = data_patterns[pattern]
            nx_data.create_dataset('core_dir', data=values['core_dir'])
            nx_data.create_dataset('slice_dir', data=values['slice_dir'])

    def __output_metadata_dict(self, data, entry):
        meta_data = data.meta_data.get_dictionary()
        entry = entry.create_group('meta_data')
        entry.attrs['NX_class'] = 'NXcollection'
        for mData in meta_data:
            nx_data = entry.create_group(mData)
            nx_data.attrs[NX_CLASS] = 'NXdata'
            nx_data.create_dataset(mData, data=meta_data[mData])

    def _close_file(self, data):
        """
        Closes the backing file and completes work
        """
        if data.backing_file is not None:
            try:
                logging.debug("Completing file %s", data.backing_file.filename)
                data.backing_file.close()
                data.backing_file = None
            except:
                pass

    def _save_data(self, data, link_type=None):
#        if data.remove is True or data.backing_file.mode == 'r':
#            link_type = None

        if link_type is None or data.remove is True:
            print "closing the file without linking", link_type, data.remove
            print data.get_name(), "\n"
            self._close_file(data)
            self.exp._barrier()
            return

        self.__add_data_links(data, link_type)
        filename = data.backing_file.filename
        entry = data.data.name
        self._close_file(data)
        self.exp._barrier()
        return entry, filename

    def __add_data_links(self, data, linkType):
        logging.info("Adding link to file %s", self.nxs_filename)
        entry = self.nxs_file['entry']
        group_name = data.data_info.get('group_name')
        self.__output_metadata(data, data.backing_file[group_name])
        filename = data.backing_file.filename.split('/')[-1]

        if linkType is 'final_result':
            name = 'final_result_' + data.get_name()
            entry[name] = \
                h5py.ExternalLink(filename, data.group_name)
        elif linkType is 'intermediate':
            name = data.group_name + '_' + data.data_info.get('name')
            entry = entry.require_group('intermediate')
            entry.attrs['NX_class'] = 'NXcollection'
            entry[name] = \
                h5py.ExternalLink(filename, data.group_name)
        else:
            raise Exception("The link type is not known")

    def _open_read_only(self, data, filename, entry):
        self.exp._barrier()
        data.backing_file = self.__open_backing_h5(filename, 'r')
        data.data = data.backing_file[entry]
        self.exp._barrier()
