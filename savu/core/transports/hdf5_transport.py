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
.. module:: hdf5_transport
   :platform: Unix
   :synopsis: Transport specific plugin list runner, passes the data to and \
       from the plugin.

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import os
import logging

from savu.core.transport_setup import MPI_setup
from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
from savu.core.transports.base_transport import BaseTransport


class Hdf5Transport(BaseTransport):

    def __init__(self):
        super(Hdf5Transport, self).__init__()
        os.environ['savu_mode'] = 'hdf5'
        self.count = 0

    def _transport_initialise(self, options):
        MPI_setup(options)
        self.exp_coll = None
        self.data_flow = []
        self.files = []

    def _transport_update_plugin_list(self):
        plugin_list = self.exp.meta_data.plugin_list
        saver_idx = plugin_list._get_savers_index()
        remove = []

        # check the saver plugin and turn off if it is hdf5
        for idx in saver_idx:
            # This saver id is not a location in the plugin list
            if idx <= len(plugin_list.plugin_list):
                if plugin_list.plugin_list[idx]['name'] == 'Hdf5Saver':
                    remove.append(idx)
        for idx in sorted(remove, reverse=True):
            plugin_list._remove(idx)

    def _transport_pre_plugin_list_run(self):
        # run through the experiment (no processing) and create output files
        self.hdf5 = Hdf5Utils(self.exp)
        self.exp_coll = self.exp._get_collection()
        self.data_flow = self.exp.meta_data.plugin_list._get_dataset_flow()
        n_plugins = list(range(len(self.exp_coll['datasets'])))

        for i in n_plugins:
            self.exp._set_experiment_for_current_plugin(i)
            self.files.append(
                self._get_filenames(self.exp_coll['plugin_dict'][i]))
            self._set_file_details(self.files[i])
            self._setup_h5_files()  # creates the hdf5 files

    def _transport_pre_plugin(self):
        count = self.exp.meta_data.get('nPlugin')
        self._set_file_details(self.files[count])

    def _transport_post_plugin(self):
        for data in list(self.exp.index['out_data'].values()):
            if not data.remove:
                msg = self.__class__.__name__ + "_transport_post_plugin."
                self.exp._barrier(msg=msg)
                if self.exp.meta_data.get('process') == \
                        len(self.exp.meta_data.get('processes'))-1:
                    self._populate_nexus_file(data)
                    # check what iteration number we are on
                    if self.exp.meta_data.get('iteration_number') == 0:
                        # link output h5 file as normal
                        self.hdf5._link_datafile_to_nexus_file(data)
                    else:
                        # don't link output h5 file, because it has already been
                        # linked when iteration 0 was completed
                        info_msg = f"Not linking intermediate h5 file, on " \
                            f"iteration" \
                            f"{self.exp.meta_data.get('iteration_number')}"
                        print(info_msg)
                self.exp._barrier(msg=msg)
                if self.exp.meta_data.get('is_in_iterative_loop'):
                    # reopen file with write permissiosn still present
                    self.hdf5._reopen_file(data, 'r+')
                else:
                    # reopen file as read-only
                    self.hdf5._reopen_file(data, 'r')

    def _transport_terminate_dataset(self, data):
        self.hdf5._close_file(data)

    def _transport_checkpoint(self):
        """ The framework has determined it is time to checkpoint.  What
        should this transport mechanism do?"""
        cp = self.exp.checkpoint
        with self.hdf5._open_backing_h5(cp._file, 'a', mpi=False) as f:
            self._metadata_dump(f, 'in_data')
            self._metadata_dump(f, 'out_data')

    def _metadata_dump(self, f, gname):
        if gname in list(f.keys()):
            del f[gname]

        for data in list(self.exp.index[gname].values()):
            name = data.get_name()
            entry = f.require_group(gname + '/' + name)
            self._output_metadata(data, entry, name, dump=True)

    def _transport_kill_signal(self):
        """ An opportunity to send a kill signal to the framework.  Return
        True or False. """
        path = self.exp.meta_data.get('out_path')
        killsignal = os.path.join(path, 'killsignal')
        # jump to the end of the plugin run!

        if os.path.exists(killsignal):
            self.exp.meta_data.set('killsignal', True)
            logging.debug("***************** killsignal sent ****************")
            return True
        return False

    def _transport_cleanup(self, i):
        """ Any remaining cleanup after kill signal sent """
        n_plugins = len(self.exp_coll['datasets'])
        for i in range(i, n_plugins):
            self.exp._set_experiment_for_current_plugin(i)
            for data in list(self.exp.index['out_data'].values()):
                self.hdf5._close_file(data)

