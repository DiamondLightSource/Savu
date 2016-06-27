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
.. module:: experiment_collection
   :platform: Unix
   :synopsis: Contains the Experiment class and all possible experiment \
   collections from which Experiment can inherit at run time.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import os
import logging
import copy
import h5py
from mpi4py import MPI

import savu.core.utils as cu
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
        self.index = {"in_data": {}, "out_data": {}, "mapping": {}}
        self.nxs_file = None

    def get_meta_data(self, entry):
        """ Get the meta data dictionary. """
        return self.meta_data.get_meta_data(entry)

    def __meta_data_setup(self, process_file):
        self.meta_data.plugin_list = PluginList()

        try:
            rtype = self.meta_data.get_meta_data('run_type')
            if rtype is 'test':
                self.meta_data.plugin_list.plugin_list = \
                    self.meta_data.get_meta_data('plugin_list')
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

    def _set_nxs_filename(self):
        folder = self.meta_data.get_meta_data('out_path')
        fname = os.path.basename(folder.split('_')[-1]) + '_processed.nxs'
        filename = os.path.join(folder, fname)
        self.meta_data.set_meta_data("nxs_filename", filename)

        if self.meta_data.get_meta_data("mpi") is True:
            self.nxs_file = h5py.File(filename, 'w', driver='mpio',
                                      comm=MPI.COMM_WORLD)
        else:
            self.nxs_file = h5py.File(filename, 'w')

    def __remove_dataset(self, data_obj):
        data_obj._close_file()
        del self.index["out_data"][data_obj.data_info.get_meta_data('name')]

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
        if self.meta_data.get_meta_data('mpi') is True:
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
