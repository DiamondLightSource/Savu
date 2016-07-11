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

from savu.core.transport_control import TransportControl
from savu.core.transport_setup import MPI_setup


class Hdf5Transport(TransportControl):

    def _transport_initialise(self, options):
        MPI_setup(options)

    def _transport_pre_plugin_list_run(self):
        # run through the experiment (no processing) and create output files
        # (final plugin files are automatically created.)
        exp_coll = self.exp._get_experiment_collection()
        for i in range(len(exp_coll['datasets'])-1):
            self.exp._set_experiment_for_current_plugin(i)
            exp_coll['saver_plugin'].setup()  # creates the hdf5 files

    def _transport_post_plugin(self):
        saver = self.exp._get_experiment_collection()['saver_plugin']
        for data in self.exp.index["out_data"].values():
            if data.remove is False:
                entry, fname = \
                    saver._save_data(data, self.exp.meta_data.get("link_type"))
                saver._open_read_only(data, fname, entry)
            else:
                saver._save_data(data, self.exp.meta_data.get("link_type"))
