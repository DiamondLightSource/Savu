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

import logging
import os

from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
from savu.core.transports.base_transport import BaseTransport
from savu.core.transport_setup import MPI_setup


class Hdf5Transport(BaseTransport):

    def _transport_initialise(self, options):
        MPI_setup(options)
        self.exp_coll = None
        self.files = []

    def _transport_pre_plugin_list_run(self):
        # run through the experiment (no processing) and create output files
        self.hdf5 = Hdf5Utils(self.exp)
        self.exp_coll = self.exp._get_experiment_collection()
        # check the saver plugin and turn off if it is hdf5
        self.__check_saver()
        n_plugins = range(len(self.exp_coll['datasets']))
        for i in n_plugins:
            self.exp._set_experiment_for_current_plugin(i)
            self.files.append(
                self.__get_filenames(self.exp_coll['plugin_dict'][i], i+1))
            self.__set_file_details(self.files[i])
            self.__setup_h5_files()  # creates the hdf5 files

    def _transport_pre_plugin(self):
        count = self.exp.meta_data.get('nPlugin')
        self.__set_file_details(self.files[count])

    def _transport_post_plugin(self):
        for data in self.exp.index['out_data'].values():
            self.hdf5._link_datafile_to_nexus_file(data)
            self.hdf5._open_read_only(data)

    def _transport_terminate_dataset(self, data):
        self.hdf5._close_file(data)

    def __setup_h5_files(self):
        out_data_dict = self.exp.index["out_data"]
        current_and_next = [0]*len(out_data_dict)
        if 'current_and_next' in self.exp.meta_data.get_dictionary():
            current_and_next = self.exp.meta_data.get('current_and_next')

        count = 0
        for key in out_data_dict.keys():
            out_data = out_data_dict[key]
            filename = self.exp.meta_data.get(["filename", key])
            logging.debug("creating the backing file %s", filename)
            out_data.backing_file = self.hdf5._open_backing_h5(filename, 'w')
            out_data.group_name, out_data.group = self.hdf5._create_entries(
                out_data, key, current_and_next[count])
            count += 1

    def __check_saver(self):
        plugin_list = self.exp.meta_data.plugin_list
        saver_plugin = plugin_list.plugin_list[-1]['name']
        if saver_plugin == 'Hdf5TomoSaver':
            plugin_list._set_saver_plugin_status(False)

    def __set_file_details(self, files):
        self.exp.meta_data.set('link_type', files['link'])
        self.exp.meta_data.set('filename', {})
        self.exp.meta_data.set('group_name', {})
        for key in self.exp.index['out_data'].keys():
            self.exp.meta_data.set(['filename', key], files['filename'][key])
            self.exp.meta_data.set(['group_name', key],
                                   files['group_name'][key])

    def _transport_get_n_processing_plugins(self):
        p_list = self.exp.meta_data.plugin_list
        n_plugins = p_list._get_n_processing_plugins()
        if p_list.plugin_list[-1]['name'] == 'Hdf5TomoSaver':
            return n_plugins - 1
        return n_plugins

    def __get_filenames(self, plugin_dict, count):
        plugin_list = self.exp.meta_data.plugin_list
        nPlugins = self._transport_get_n_processing_plugins()
        saver = plugin_list._get_saver_plugin_status()
        files = {"filename": {}, "group_name": {}}
        for key in self.exp.index["out_data"].keys():
            name = key + '_p' + str(count) + '_' + \
                plugin_dict['id'].split('.')[-1] + '.h5'
            if count is nPlugins:
                out_path = self.exp.meta_data.get('out_path')
            else:
                out_path = self.exp.meta_data.get('inter_path')
            filename = os.path.join(out_path, name)
            group_name = "%i-%s-%s" % (count, plugin_dict['name'], key)
            self.exp._barrier()
            files["filename"][key] = filename
            files["group_name"][key] = group_name
        link = "final_result" if count is nPlugins-saver else "intermediate"
        files["link"] = link
        return files
