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
.. module:: basic_transport
   :platform: Unix
   :synopsis: Transports data to and from file at the beginning and end of the\
   process list respectively.

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import os

from savu.core.transport_setup import MPI_setup
from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
from savu.core.transports.hdf5_transport import Hdf5Transport
from savu.core.transports.base_transport import BaseTransport


class BasicTransport(BaseTransport):

    def __init__(self):
        super(BasicTransport, self).__init__()
        self.global_data = True
        self.h5trans = Hdf5Transport()
        self.data_flow = None
        self.count = 0
        self.hdf5_flag = True

    def _transport_initialise(self, options):
        MPI_setup(options)
        # initially reading from a hdf5 file so Hdf5TransportData will be used
        # for all datasets created in a loader
        options['transport'] = 'hdf5'
        os.environ['savu_mode'] = 'basic'

    def _transport_pre_plugin_list_run(self):
        # loaders have completed now revert back to BasicTransport, so any
        # output datasets created by a plugin will use this.
        self.hdf5 = Hdf5Utils(self.exp)
        self.data_flow = self.exp.meta_data.plugin_list._get_dataset_flow()
        plist = self.exp.meta_data.plugin_list
        self.n_plugins = plist._get_n_processing_plugins()
        self.final_dict = plist.plugin_list[-1]
        if self.n_plugins != 1:
            self.exp.meta_data.set('transport', 'basic')

    def _transport_pre_plugin(self):
        trans = self.exp.meta_data.get('transport')
        if self.count == self.n_plugins - 1 or trans == 'hdf5':
            self.__set_hdf5_transport()

    def _transport_post_plugin(self):
        # revert back to basic if a temporary transport mechanism was used
        if self.hdf5_flag:
            self.__unset_hdf5_transport()

        if self.count == self.n_plugins - 2:
            self.exp.meta_data.set('transport', 'hdf5')

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

    def _transport_terminate_dataset(self, data):
        if data.backing_file:
            self.hdf5._close_file(data)
