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
import copy
import h5py
import logging
from mpi4py import MPI

import savu.plugins.utils as pu
from savu.data.meta_data import MetaData
from savu.data.plugin_list import PluginList
from savu.data.data_structures.data import Data
from savu.core.checkpointing import Checkpointing
from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
import savu.plugins.loaders.utils.yaml_utils as yaml


class Experiment(object):
    """
    One instance of this class is created at the beginning of the
    processing chain and remains until the end.  It holds the current data
    object and a dictionary containing all metadata.
    """

    def __init__(self, options):
        self.meta_data = MetaData(options)
        self.__set_system_params()
        self.checkpoint = Checkpointing(self)
        self.__meta_data_setup(options["process_file"])
        self.experiment_collection = {}
        self.index = {"in_data": {}, "out_data": {}}
        self.initial_datasets = None
        self.plugin = None
        self._transport = None
        self._barrier_count = 0

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
            template = self.meta_data.get('template')
            self.meta_data.plugin_list._populate_plugin_list(process_file,
                                                             template=template)

    def create_data_object(self, dtype, name, override=True):
        """ Create a data object.

        Plugin developers should apply this method in loaders only.

        :params str dtype: either "in_data" or "out_data".
        """
        if name not in self.index[dtype].keys() or override:
            self.index[dtype][name] = Data(name, self)
            data_obj = self.index[dtype][name]
            data_obj._set_transport_data(self.meta_data.get('transport'))
        return self.index[dtype][name]

    def _experiment_setup(self, transport):
        """ Setup an experiment collection.
        """
        n_loaders = self.meta_data.plugin_list._get_n_loaders()
        plugin_list = self.meta_data.plugin_list
        plist = plugin_list.plugin_list
        self.__set_transport(transport)
        # load the loader plugins
        self._set_loaders()
        # load the saver plugin and save the plugin list
        self.experiment_collection = {'plugin_dict': [],
                                      'datasets': []}
        self._barrier()
        self._check_checkpoint()
        self._barrier()
        checkpoint = self.meta_data.get('checkpoint')
        if self.meta_data.get('process') == \
                len(self.meta_data.get('processes'))-1 and not checkpoint:
            plugin_list._save_plugin_list(self.meta_data.get('nxs_filename'))
            # links the input data to the nexus file
            self._add_input_data_to_nxs_file(transport)
        # Barrier 13
        self._barrier()

        n_plugins = plugin_list._get_n_processing_plugins()
        count = 0
        # first run through of the plugin setup methods
        for plugin_dict in plist[n_loaders:n_loaders+n_plugins]:
            data = self.__plugin_setup(plugin_dict, count)
            self.experiment_collection['datasets'].append(data)
            self.experiment_collection['plugin_dict'].append(plugin_dict)
            self._merge_out_data_to_in()
            count += 1
        self._reset_datasets()

    def __set_transport(self, transport):
        self._transport = transport

    def _get_transport(self):
        return self._transport

    def __set_system_params(self):
        sys_file = self.meta_data.get('system_params')
        import sys
        if sys_file is None:
            # look in conda environment to see which version is being used
            savu_path = sys.modules['savu'].__path__[0]
            sys_files = os.path.join(
                    os.path.dirname(savu_path), 'system_files')
            subdirs = os.listdir(sys_files)
            sys_folder = 'dls' if len(subdirs) > 1 else subdirs[0]
            fname = 'system_parameters.yml'
            sys_file = os.path.join(sys_files, sys_folder, fname)
        logging.info('Using the system parameters file: %s', sys_file)
        self.meta_data.set('system_params', yaml.read_yaml(sys_file))

    def _check_checkpoint(self):
        # if checkpointing has been set but the nxs file doesn't contain an
        # entry then remove checkpointing (as the previous run didn't get far
        # enough to require it).
        if self.meta_data.get('checkpoint'):
            with h5py.File(self.meta_data.get('nxs_filename'), 'r') as f:
                if 'entry' not in f:
                    self.meta_data.set('checkpoint', None)

    def _set_loaders(self):
        n_loaders = self.meta_data.plugin_list._get_n_loaders()
        plugin_list = self.meta_data.plugin_list.plugin_list
        for i in range(n_loaders):
            pu.plugin_loader(self, plugin_list[i])
        self.initial_datasets = copy.deepcopy(self.index['in_data'])

    def _add_input_data_to_nxs_file(self, transport):
        # save the loaded data to file
        h5 = Hdf5Utils(self)
        for name, data in self.index['in_data'].items():
            self.meta_data.set(['link_type', name], 'input_data')
            self.meta_data.set(['group_name', name], name)
            self.meta_data.set(['filename', name], data.backing_file)
            transport._populate_nexus_file(data)
            h5._link_datafile_to_nexus_file(data)

    def _reset_datasets(self):
        self.index['in_data'] = self.initial_datasets

    def __plugin_setup(self, plugin_dict, count):
        """ Determine plugin specific information.
        """
        plugin_id = plugin_dict["id"]
        logging.debug("Loading plugin %s", plugin_id)
        # Run main_setup method
        plugin = pu.plugin_loader(self, plugin_dict)
        plugin._revert_preview(plugin.get_in_datasets())
        # Populate the metadata
        plugin._clean_up()
        data = self.index['out_data'].copy()
        return data

    def _get_experiment_collection(self):
        return self.experiment_collection

    def _set_experiment_for_current_plugin(self, count):
        datasets_list = self.meta_data.plugin_list._get_datasets_list()[count:]
        exp_coll = self._get_experiment_collection()
        self.index['out_data'] = exp_coll['datasets'][count]
        if datasets_list:
            self._get_current_and_next_patterns(datasets_list)
        self.meta_data.set('nPlugin', count)

    def _get_current_and_next_patterns(self, datasets_lists):
        """ Get the current and next patterns associated with a dataset
        throughout the processing chain.
        """
        current_datasets = datasets_lists[0]
        patterns_list = {}
        for current_data in current_datasets['out_datasets']:
            current_name = current_data['name']
            current_pattern = current_data['pattern']
            next_pattern = self.__find_next_pattern(datasets_lists[1:],
                                                    current_name)
            patterns_list[current_name] = \
                {'current': current_pattern, 'next': next_pattern}
        self.meta_data.set('current_and_next', patterns_list)

    def __find_next_pattern(self, datasets_lists, current_name):
        next_pattern = []
        for next_data_list in datasets_lists:
            for next_data in next_data_list['in_datasets']:
                if next_data['name'] == current_name:
                    next_pattern = next_data['pattern']
                    return next_pattern
        return next_pattern

    def _set_nxs_filename(self):
        folder = self.meta_data.get('out_path')
        fname = self.meta_data.get('datafile_name') + '_processed.nxs'
        filename = os.path.join(folder, fname)
        self.meta_data.set('nxs_filename', filename)

        if self.meta_data.get('process') == 1:
            if self.meta_data.get('bllog'):
                log_folder_name = self.meta_data.get('bllog')
                log_folder = open(log_folder_name, 'a')
                log_folder.write(os.path.abspath(filename) + '\n')
                log_folder.close()

    def _clear_data_objects(self):
        self.index["out_data"] = {}
        self.index["in_data"] = {}

    def _merge_out_data_to_in(self):
        for key, data in self.index["out_data"].items():
            if data.remove is False:
                self.index['in_data'][key] = data
        self.index["out_data"] = {}

    def _finalise_experiment_for_current_plugin(self):
        finalise = {}
        # populate nexus file with out_dataset information and determine which
        # datasets to remove from the framework.
        finalise['remove'] = []
        finalise['keep'] = []

        for key, data in self.index['out_data'].items():
            if data.remove is True:
                finalise['remove'].append(data)
            else:
                finalise['keep'].append(data)

        # find in datasets to replace
        finalise['replace'] = []
        for out_name in self.index['out_data'].keys():
            if out_name in self.index['in_data'].keys():
                finalise['replace'].append(self.index['in_data'][out_name])

        return finalise

    def _reorganise_datasets(self, finalise):
        # unreplicate replicated in_datasets
        self.__unreplicate_data()

        # delete all datasets for removal
        for data in finalise['remove']:
            del self.index["out_data"][data.data_info.get('name')]

        # Add remaining output datasets to input datasets
        for name, data in self.index['out_data'].items():
            data.get_preview().set_preview([])
            self.index["in_data"][name] = copy.deepcopy(data)
        self.index['out_data'] = {}

    def __unreplicate_data(self):
        in_data_list = self.index['in_data']
        from savu.data.data_structures.data_types.replicate import Replicate
        for in_data in in_data_list.values():
            if isinstance(in_data.data, Replicate):
                in_data.data = in_data.data.reset()

    def _set_all_datasets(self, name):
        data_names = []
        for key in self.index["in_data"].keys():
            if 'itr_clone' not in key:
                data_names.append(key)
        return data_names

    def _barrier(self, communicator=MPI.COMM_WORLD, msg=''):
        comm_dict = {'comm': communicator}
        if self.meta_data.get('mpi') is True:
            logging.debug("Barrier %d: %d processes expected: %s",
                          self._barrier_count, communicator.size, msg)
            comm_dict['comm'].barrier()
        self._barrier_count += 1

    def log(self, log_tag, log_level=logging.DEBUG):
        """
        Log the contents of the experiment at the specified level
        """
        logging.log(log_level, "Experimental Parameters for %s", log_tag)
        for key, value in self.index["in_data"].items():
            logging.log(log_level, "in data (%s) shape = %s", key,
                        value.get_shape())
        for key, value in self.index["in_data"].items():
            logging.log(log_level, "out data (%s) shape = %s", key,
                        value.get_shape())
