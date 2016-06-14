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
import h5py
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

    def _experiment_setup(self):
        n_loaders = self.meta_data.plugin_list._get_n_loaders()
        plugin_list = self.meta_data.plugin_list.plugin_list

        logging.debug("generating all output files")
        in_objs = []
        out_objs = []
        datasets_list = self.meta_data.plugin_list._get_datasets_list()
        plugins_inst = []

        count = n_loaders

        for i in range(n_loaders):
            pu.plugin_loader(self, plugin_list[i])

        for plugin_dict in plugin_list[n_loaders:-1]:
            self._get_current_and_next_patterns(
                datasets_list[count-n_loaders:])
            plugin_id = plugin_dict["id"]
            logging.info("Loading plugin %s", plugin_id)
            plugin = pu.plugin_loader(self, plugin_dict)
            plugins_inst.append(plugin)
            plugin._revert_preview(plugin.get_in_datasets())
            self.__set_filenames(plugin, plugin_id, count)

            in_objs.append(self.index['in_data'].copy())
            out_objs.append(self.index["out_data"].copy())
            self._merge_out_data_to_in()
            count += 1

        self.meta_data.delete('current_and_next')
        self.__set_experiment_collection(in_objs, out_objs, plugins_inst)

    def __set_experiment_collection(self, in_list, out_list, plugin_list):
        print("setting the experiment collection", in_list, out_list, plugin_list)
        self.experiment_collection['in_datasets'] = in_list
        self.experiment_collection['out_datasets'] = out_list
        self.experiment_collection['plugin_list'] = plugin_list

    def _get_experiment_collection(self):
        temp = self.experiment_collection
        return temp['in_datasets'], temp['out_datasets'], temp['plugin_list']

    def __set_filenames(self, plugin, plugin_id, count):
        n_loaders = self.meta_data.plugin_list.n_loaders
        nPlugins = self.meta_data.plugin_list.n_plugins - n_loaders - 1
        self.meta_data.set("filename", {})
        self.meta_data.set("group_name", {})
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
            self.meta_data.set(["filename", key], filename)
            self.meta_data.set(["group_name", key], group_name)

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

    def _set_nxs_filename(self):
        folder = self.meta_data.get('out_path')
        fname = os.path.basename(folder.split('_')[-1]) + '_processed.nxs'
        filename = os.path.join(folder, fname)
        self.meta_data.set("nxs_filename", filename)

        if self.meta_data.get("mpi") is True:
            self.nxs_file = h5py.File(filename, 'w', driver='mpio',
                                      comm=MPI.COMM_WORLD)
        else:
            self.nxs_file = h5py.File(filename, 'w')

    def __remove_dataset(self, data_obj):
        data_obj._close_file()
        del self.index["out_data"][data_obj.data_info.get('name')]

    def _clear_data_objects(self):
        self.index["out_data"] = {}
        self.index["in_data"] = {}

    def _merge_out_data_to_in(self):
        print("in merge out data to in", self.index["out_data"])
        for key, data in self.index["out_data"].iteritems():
            if data.remove is False:
                if key in self.index['in_data'].keys():
                    data.meta_data._set_dictionary(
                        self.index['in_data'][key].meta_data.get_dictionary())
                self.index['in_data'][key] = data
        self.index["out_data"] = {}

    def _reorganise_datasets(self, out_data_objs, link_type):
        out_data_list = self.index["out_data"]
        self.__close_unwanted_files(out_data_list)
        self.__remove_unwanted_data(out_data_objs)

        self._barrier()
        self.__copy_out_data_to_in_data(link_type)

        self._barrier()
        self.index['out_data'] = {}

    def __remove_unwanted_data(self, out_data_objs):
        for out_objs in out_data_objs:
            if out_objs.remove is True:
                self.__remove_dataset(out_objs)

    def __close_unwanted_files(self, out_data_list):
        for out_objs in out_data_list:
            if out_objs in self.index["in_data"].keys():
                self.index["in_data"][out_objs]._close_file()

    def __copy_out_data_to_in_data(self, link_type):
        for key in self.index["out_data"]:
            output = self.index["out_data"][key]
            output._save_data(link_type)
            self.index["in_data"][key] = copy.deepcopy(output)

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
