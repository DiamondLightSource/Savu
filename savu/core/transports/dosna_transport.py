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
.. module:: dosna_transport
   :platform: Unix
   :synopsis: Transports data using DosNa(which provides several storing \
   backends) at the beginning and end of the process list respectively.

.. moduleauthor:: Emilio Perez Juarez <scientificsoftware@diamond.ac.uk>

"""

import logging

from savu.core.transport_setup import MPI_setup
from savu.core.transports.base_transport import BaseTransport
from savu.core.transports.hdf5_transport import Hdf5Transport
from savu.data.chunking import Chunking
from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils

import dosna as dn

log = logging.getLogger(__name__)

DEFAULT_CONNECTION = "savu-data"
DEFAULT_BACKEND = "ceph"
DEFAULT_ENGINE = "mpi"

class DosnaTransport(BaseTransport):
    """Transport implementation to use DosNa for managing storage and
    chunking"""

    def __init__(self):
        super(DosnaTransport, self).__init__()
        self.dosna_connection = None
        self.global_data = True
        self.h5trans = Hdf5Transport()
        self.data_flow = None
        self.count = 0
        self.hdf5 = None
        self.hdf5_flag = True
        self.files = []
        self.final_dict = None
        self.dataset_cache = []
        self.n_plugins = 0

    def _transport_initialise(self, options):
        MPI_setup(options)

        backend = options.get("dosna_backend") or DEFAULT_BACKEND
        engine = options.get("dosna_engine") or DEFAULT_ENGINE
        dosna_connection_name = options.get("dosna_connection") \
            or DEFAULT_CONNECTION
        dosna_connection_options = options.get("dosna_connection_options")

        dosna_options = {}

        dosna_options.update(dict(item.split('=')
                             for item in dosna_connection_options))
        log.debug("DosNa is using backend %s engine %s and options %s",
                  backend, engine, dosna_options)
        dn.use(engine, backend)
        self.dosna_connection = dn.Connection(dosna_connection_name,
                                              **dosna_options)
        self.dosna_connection.connect()
        # initially reading from a hdf5 file so Hdf5TransportData will be used
        # for all datasets created in a loader
        options['transport'] = 'hdf5'

    def _transport_update_plugin_list(self):
        plugin_list = self.exp.meta_data.plugin_list
        saver_idx = plugin_list._get_savers_index()
        remove = []

        # check the saver plugin and turn off if it is hdf5
        for idx in saver_idx:
            if plugin_list.plugin_list[idx]['name'] == 'Hdf5Saver':
                remove.append(idx)
        for idx in sorted(remove, reverse=True):
            plugin_list._remove(idx)

    def _transport_pre_plugin_list_run(self):
        # loaders have completed now revert back to DosnaTransport, so any
        # output datasets created by a plugin will use this.
        self.hdf5 = Hdf5Utils(self.exp)
        exp_coll = self.exp._get_collection()
        self.data_flow = self.exp.meta_data.plugin_list._get_dataset_flow()
        #self.exp.meta_data.set('transport', 'dosna')
        plist = self.exp.meta_data.plugin_list
        self.n_plugins = plist._get_n_processing_plugins()
        self.final_dict = plist.plugin_list[-1]
        for plugin_index in range(self.n_plugins):
            self.exp._set_experiment_for_current_plugin(plugin_index)
            self.files.append(
                self._get_filenames(exp_coll['plugin_dict'][plugin_index]))
            self._set_file_details(self.files[plugin_index])
            self._setup_dosna_objects()  # creates the dosna objects

        if self.n_plugins != 1:
            self.exp.meta_data.set('transport', 'dosna')

    def _transport_post_plugin_list_run(self):
        if not self.dosna_connection:
            return
        for dataset in self.dataset_cache:
            self.dosna_connection.del_dataset(dataset.name)
        self.dataset_cache = []
        self.dosna_connection.disconnect()
        self.dosna_connection = None

    def _transport_terminate_dataset(self, data):
        if self.exp.meta_data.get('transport') == "hdf5":
            self.hdf5._close_file(data)

    @staticmethod
    def _extract_digits(data):
        result = []
        for char in data:
            if ord(char) in range(ord('0'), ord('9') + 1):
                result.append(char)
        return "".join(result)

    def _create_dosna_dataset(self, object_id, data, key, current_and_next):
        group_name = self.exp.meta_data.get(["group_name", key])
        data.data_info.set('group_name', group_name)
        try:
            group_name = group_name + '_' + data.name
        except AttributeError:
            pass

        shape = data.get_shape()
        dataset_name = "{}_{}".format(group_name,
                                      self._extract_digits(object_id))

        if current_and_next == 0:
            data.data = self.dosna_connection.create_dataset(dataset_name,
                                                             shape,
                                                             data.dtype)
        else:
            chunking = Chunking(self.exp, current_and_next)
            chunks = chunking._calculate_chunking(shape, data.dtype)
            data.data = self.dosna_connection.create_dataset(dataset_name,
                                                             shape,
                                                             data.dtype,
                                                             chunk_size=chunks)
        self.dataset_cache.append(data.data)

    def _setup_dosna_objects(self):
        out_data_dict = self.exp.index["out_data"]

        current_and_next = [0]*len(out_data_dict)
        if 'current_and_next' in self.exp.meta_data.get_dictionary():
            current_and_next = self.exp.meta_data.get('current_and_next')

        for key in list(out_data_dict.keys()):
            out_data = out_data_dict[key]
            filename = self.exp.meta_data.get(["filename", key])
            self._create_dosna_dataset(filename, out_data, key,
                                       current_and_next[key])

    def _transport_pre_plugin(self):
        if self.count == self.n_plugins - 1:
            self.__set_hdf5_transport()

    def _transport_post_plugin(self):
        # revert back to basic if a temporary transport mechanism was used
        if self.hdf5_flag:
            self.__unset_hdf5_transport()

        if self.count == self.n_plugins - 2:
            self.exp.meta_data.set('transport', 'dosna')

        if self.count == self.n_plugins - 1:  # final plugin
            self.h5trans.exp = self.exp
            self.h5trans.hdf5 = Hdf5Utils(self.exp)
            self.h5trans._transport_post_plugin()

        self.count += 1

    def __set_hdf5_transport(self):
        self.hdf5_flag = True
        self.exp.meta_data.set('transport', 'hdf5')
        files = self._get_filenames(self.final_dict)
        self._set_file_details(files)
        self._setup_h5_files()

    def __unset_hdf5_transport(self):
        self.exp.meta_data.set('transport', 'basic')
        self.hdf5_flag = False
