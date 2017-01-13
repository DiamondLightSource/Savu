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
        self.hdf5 = None

    def _transport_pre_plugin_list_run(self):
        # run through the experiment (no processing) and create output files
        plugin_id = 'savu.plugins.savers.hdf5_tomo_saver'
        self.hdf5 = pu.plugin_loader(self.exp, {'id': plugin_id, 'data': {}})
        exp_coll = self.exp._get_experiment_collection()

        n_plugins = len(exp_coll['datasets'])
        for i in n_plugins:
            self.exp._set_experiment_for_current_plugin(i)
            
            exp_coll['files']['group_name']
            self.hdf5.setup()  # creates the hdf5 files
#
#

#        files = {"filename": {}, "group_name": {}}
#        for key in self.index["out_data"].keys():
#
#            name = key + '_p' + str(count) + '_' + \
#                plugin_id.split('.')[-1] + '.h5'
#            if count is nPlugins:
#                out_path = self.meta_data.get('out_path')
#            else:
#                out_path = self.meta_data.get('inter_path')
#            filename = os.path.join(out_path, name)
#            group_name = "%i-%s-%s" % (count, plugin.name, key)
#            self._barrier()
#            files["filename"][key] = filename
#            files["group_name"][key] = group_name
#
#        link = "final_result" if count+1 is nPlugins else "intermediate"
#        files["link"] = link
#        return files






    def _transport_post_plugin(self):
        for data in self.exp.index["out_data"].values():
            entry, fname = self.saver._save_data(
                data, self.exp.meta_data.get("link_type"))
            self.hdf5._open_read_only(data, fname, entry)

    def _transport_post_plugin_list_run(self):
        for data in self.exp.index["in_data"].values():
            self.hdf5._save_data(data, self.exp.meta_data.get("link_type"))

    def _transport_finalise_dataset(self, data):
        # the dataset is no longer required by the framework
        self.hdf5._save_data(data, self.exp.meta_data.get("link_type"))
