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

import savu.plugins.utils as pu
from savu.core.transports.base_transport import BaseTransport
from savu.core.transport_setup import MPI_setup


class Hdf5Transport(BaseTransport):

    def _transport_initialise(self, options):
        MPI_setup(options)
        self.saver = None

    def _transport_pre_plugin_list_run(self):
        self.exp._barrier()
        # run through the experiment (no processing) and create output files
        plugin_id = 'savu.plugins.savers.hdf5_tomo_saver'
        self.saver = pu.plugin_loader(self.exp, {'id': plugin_id, 'data': {}})
        exp_coll = self.exp._get_experiment_collection()
        for i in range(len(exp_coll['datasets'])):
            self.exp._set_experiment_for_current_plugin(i)
            self.saver.setup()  # creates the hdf5 files
            self.exp._barrier()

    def _transport_post_plugin(self):
        # This should only happen if there is a .nxs file.
        self.exp._barrier()
        for data in self.exp.index["out_data"].values():
            if data.remove is False:
                entry, fname = self.saver._save_data(
                    data, self.exp.meta_data.get("link_type"))
                self.saver._open_read_only(data, fname, entry)
            else:
                self.saver._save_data(
                    data, self.exp.meta_data.get("link_type"))
            self.exp._barrier()
