# -*- coding: utf-8 -*-
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
.. module:: experiment
   :platform: Unix
   :synopsis: Contains information specific to the entire experiment.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""
import os
import logging
import copy
from mpi4py import MPI

import savu.core.utils as cu
import savu.plugins.utils as pu
from savu.data.plugin_list import PluginList
from savu.data.data_structures.data import Data
from savu.data.meta_data import MetaData


class Experiment(object):
    """
    One instance of this class is created at the beginning of the
    processing chain and remains until the end.  It holds the current data
    object and a dictionary containing all metadata.
    """

    def __init__(self, options):
        self.meta_data = MetaData(options)
        self.__meta_data_setup(options["process_file"])
        self.experiment_collection = {}
        self.index = {"in_data": {}, "out_data": {}}
        self.nxs_file = None

    def get(self, entry):
        """ Get the meta data dictionary. """
        return self.meta_data.get(entry)

    def __meta_data_setup(self, process_file):
        self.meta_data.plugin_list = PluginList()

        try:
            rtype = self.meta_data.get('run_type')
            if rtype is 'test':
                self.meta_data.plugin_list.plugin_list = \
                    self.meta_data.get('plugin_list')
            else:
                raise Exception('the run_type is unknown in Experiment class')
        except KeyError:
            self.meta_data.plugin_list._populate_plugin_list(process_file)

    def create_data_object(self, dtype, name):
        """ Create a data object.

        Plugin developers should apply this method in loaders only.

        :params str dtype: either "in_data" or "out_data".
        """
        bases = []
        try:
            self.index[dtype][name]
        except KeyError:
            self.index[dtype][name] = Data(name, self)
            data_obj = self.index[dtype][name]
            bases.append(data_obj._get_transport_data())
            cu.add_base_classes(data_obj, bases)
        return self.index[dtype][name]

    def _experiment_setup(self):
        """ Setup the experiment by creating lists of in/out datasets, \
        associated plugin datasets, and a potential output filename for each \
        plugin.  Group this information together in an experiment collection.
        """
        n_loaders = self.meta_data.plugin_list._get_n_loaders()
        plugin_list = self.meta_data.plugin_list.plugin_list

        logging.debug("generating all output files")
        in_objs = []
        out_objs = []
        plugin_inst = []
        file_list = []

        # load the loader plugins
        for i in range(n_loaders):
            pu.plugin_loader(self, plugin_list[i])

        # load the saver plugin and save the plugin list
        saver = pu.plugin_loader(self, plugin_list[-1])
        logging.debug("Saving plugin list to file.")
        self.meta_data.plugin_list._save_plugin_list(saver)

        count = 0
        for plugin_dict in plugin_list[n_loaders:-1]:
            in_data, out_data, plugin, out_file = \
                self.__plugin_setup(plugin_dict, count)
            self._merge_out_data_to_in()
            in_objs.append(in_data)
            out_objs.append(out_data)
            plugin_inst.append(plugin)
            file_list.append(out_file)
            count += 1

        self.__set_experiment_collection(in_objs, out_objs, plugin_inst,
                                         file_list, saver)

    def __plugin_setup(self, plugin_dict, count):
        """ Determine plugin specific information: in_datasets, out_datasets,
        plugin instance and output file.
        """
        plugin_id = plugin_dict["id"]
        logging.info("Loading plugin %s", plugin_id)
        plugin = pu.plugin_loader(self, plugin_dict)

        files = self.__set_filenames(plugin, plugin_id, count)
        temp_in = copy.deepcopy(self.index['in_data'])
        plugin._revert_preview(plugin.get_in_datasets())
        in_pData = self.__detach_plugin_datasets(temp_in)
        temp_out = self.index['out_data'].copy()
        out_pData = self.__detach_plugin_datasets(temp_out)
        in_data = {"data": temp_in, "pData": in_pData}
        out_data = {"data": temp_out, "pData": out_pData}
        return in_data, out_data, plugin, files

    def __detach_plugin_datasets(self, data_dict):
        pData_dict = {}
        for key in data_dict:
            pData_dict[key] = copy.deepcopy(data_dict[key]._get_plugin_data())
            data_dict[key]._clear_plugin_data()
        return pData_dict

    def __set_experiment_collection(self, in_list, out_list, plugin_list,
                                    file_list, saver):
        self.experiment_collection['in_datasets'] = in_list
        self.experiment_collection['out_datasets'] = out_list
        self.experiment_collection['plugin_list'] = plugin_list
        self.experiment_collection['file_list'] = file_list
        self.experiment_collection['saver_plugin'] = saver

    def _get_experiment_collection(self):
        return self.experiment_collection

    def __set_filenames(self, plugin, plugin_id, count):
        n_loaders = self.meta_data.plugin_list.n_loaders
        nPlugins = self.meta_data.plugin_list.n_plugins - n_loaders - 1
        files = {"filename": {}, "group_name": {}}
        for key in self.index["out_data"].keys():
            name = key + '_p' + str(count) + '_' + \
                plugin_id.split('.')[-1] + '.h5'
            if count is nPlugins:
                out_path = self.meta_data.get('out_path')
            else:
                out_path = self.meta_data.get('inter_path')
            filename = os.path.join(out_path, name)
            group_name = "%i-%s-%s" % (count, plugin.name, key)
            self._barrier()
            logging.debug("(set_filenames) Creating output file after "
                          " _barrier %s", filename)
            files["filename"][key] = filename
            files["group_name"][key] = group_name
        link = "final_result" if count is nPlugins else "intermediate"
        files["link"] = link
        return files

    def _set_experiment_details_for_current_plugin(self, count):
        datasets_list = \
            self.meta_data.plugin_list._get_datasets_list()[count:]
        exp_coll = self._get_experiment_collection()
        self._clear_data_objects()
        data_dict = {"in_data": exp_coll["in_datasets"][count],
                     "out_data": exp_coll["out_datasets"][count]}
        self.__set_data_objects(data_dict)
        self.__set_output_file(exp_coll["file_list"][count])
        self._get_current_and_next_patterns(datasets_list)

    def __set_output_file(self, out_file):
        self.meta_data.set("filename", {})
        self.meta_data.set("group_name", {})
        for key in self.index['out_data'].keys():
            self.meta_data.set("link_type", out_file["link"])
            self.meta_data.set(["filename", key], out_file["filename"][key])
            self.meta_data.set(["group_name", key],
                               out_file["group_name"][key])

    def _get_current_and_next_patterns(self, datasets_lists):
        """ Get the current and next patterns associated with a dataset
        throughout the processing chain.
        """
        current_datasets = datasets_lists[0]
        patterns_list = []
        for current_data in current_datasets['out_datasets']:
            current_name = current_data['name']
            current_pattern = current_data['pattern']
            next_pattern = self.__find_next_pattern(datasets_lists[1:],
                                                    current_name)
            patterns_list.append({'current': current_pattern,
                                  'next': next_pattern})
        self.meta_data.set('current_and_next', patterns_list)

    def __find_next_pattern(self, datasets_lists, current_name):
        next_pattern = []
        for next_data_list in datasets_lists:
            for next_data in next_data_list['in_datasets']:
                if next_data['name'] == current_name:
                    next_pattern = next_data['pattern']
                    return next_pattern
        return next_pattern

    def __set_data_objects(self, data_dict):
        for key in data_dict.keys():
            for name in data_dict[key]['data']:
                entry = data_dict[key]
                pData = entry['pData'][name]
                print "setting the plugin data"
                entry['data'][name]._set_plugin_data(pData)
                print entry['data'][name]
                print entry['data'][name]._get_plugin_data().padding
                self.index[key][name] = entry['data'][name]

    def _clear_data_objects(self):
        self.index["out_data"] = {}
        self.index["in_data"] = {}

    def _merge_out_data_to_in(self):
        for key, data in self.index["out_data"].iteritems():
            if data.remove is False:
                if key in self.index['in_data'].keys():
                    data.meta_data._set_dictionary(
                        self.index['in_data'][key].meta_data.get_dictionary())
                self.index['in_data'][key] = data
        self.index["out_data"] = {}

    def _set_all_datasets(self, name):
        data_names = []
        for key in self.index["in_data"].keys():
            data_names.append(key)
        return data_names

    def _barrier(self, communicator=MPI.COMM_WORLD):
        comm_dict = {'comm': communicator}
        if self.meta_data.get('mpi') is True:
            logging.debug("About to hit a _barrier %s", comm_dict)
            comm_dict['comm'].barrier()
            logging.debug("Past the _barrier")

    def log(self, log_tag, log_level=logging.DEBUG):
        """
        Log the contents of the experiment at the specified level
        """
        logging.log(log_level, "Experimental Parameters for %s", log_tag)
        for key, value in self.index["in_data"].iteritems():
            logging.log(log_level, "in data (%s) shape = %s", key,
                        value.get_shape())
        for key, value in self.index["in_data"].iteritems():
            logging.log(log_level, "out data (%s) shape = %s", key,
                        value.get_shape())
