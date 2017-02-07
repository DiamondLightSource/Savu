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
import numpy as np
from mpi4py import MPI

import savu.core.utils as cu
import savu.plugins.utils as pu
from savu.data.plugin_list import PluginList
from savu.data.data_structures.data import Data
from savu.data.meta_data import MetaData

NX_CLASS = 'NX_class'


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
        self.initial_datasets = None
        self.plugin = None

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
        """ Setup an experiment collection.
        """
        n_loaders = self.meta_data.plugin_list._get_n_loaders()
        plugin_list = self.meta_data.plugin_list
        plist = plugin_list.plugin_list

        # load the loader plugins
        self._set_loaders()
        # load the saver plugin and save the plugin list
        self.experiment_collection = {'plugin_dict': [],
                                      'datasets': []}
        logging.debug("Saving plugin list to file.")
        plugin_list._save_plugin_list(self.meta_data.get('nxs_filename'),
                                      exp=self)

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

    def _set_loaders(self):
        n_loaders = self.meta_data.plugin_list._get_n_loaders()
        plugin_list = self.meta_data.plugin_list.plugin_list
        for i in range(n_loaders):
            pu.plugin_loader(self, plugin_list[i])
        self.initial_datasets = copy.deepcopy(self.index['in_data'])

    def _reset_datasets(self):
        self.index['in_data'] = self.initial_datasets

    def __plugin_setup(self, plugin_dict, count):
        """ Determine plugin specific information.
        """
        plugin_id = plugin_dict["id"]
        logging.info("Loading plugin %s", plugin_id)
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
        n_loaders = self.meta_data.plugin_list._get_n_loaders()
        datasets_list = \
            self.meta_data.plugin_list._get_datasets_list()[n_loaders+count:]
        exp_coll = self._get_experiment_collection()
        self.index['out_data'] = exp_coll['datasets'][count]
        self._get_current_and_next_patterns(datasets_list)
        self.meta_data.set('nPlugin', count)

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

    def _set_nxs_filename(self):
        folder = self.meta_data.get('out_path')
        fname = os.path.basename(folder.split('_')[-1]) + '_processed.nxs'
        filename = os.path.join(folder, fname)
        self.meta_data.set('nxs_filename', filename)

        if self.meta_data.get('mpi') is True:
            self.nxs_file = \
                h5py.File(filename, 'w', driver='mpio', comm=MPI.COMM_WORLD)
        else:
            self.nxs_file = h5py.File(filename, 'w')

    def _clear_data_objects(self):
        self.index["out_data"] = {}
        self.index["in_data"] = {}

    def _merge_out_data_to_in(self):
        for key, data in self.index["out_data"].iteritems():
            if data.remove is False:
                self.index['in_data'][key] = data
        self.index["out_data"] = {}

    def _finalise_experiment_for_current_plugin(self):
        finalise = {}
        # populate nexus file with out_dataset information and determine which
        # datasets to remove from the framework.
        finalise['remove'] = []
        for key, data in self.index['out_data'].iteritems():
            self._populate_nexus_file(data)
            if data.remove is True:
                finalise['remove'].append(data)

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
        for name, data in self.index['out_data'].iteritems():
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

    def _populate_nexus_file(self, data):
        self._barrier()
        logging.info("Adding link to file %s",
                     self.meta_data.get('nxs_filename'))
        nxs_file = self.nxs_file
        nxs_entry = nxs_file['entry']
        name = data.data_info.get('name')
        group_name = self.meta_data.get(['group_name', name])
        link_type = self.meta_data.get(['link_type', name])

        if link_type is 'final_result':
            plugin_entry = \
                nxs_entry.create_group('final_result_' + data.get_name())
            plugin_entry.attrs[NX_CLASS] = 'NXdata'
        elif link_type is 'intermediate':
            link = nxs_entry.require_group(link_type)
            link.attrs[NX_CLASS] = 'NXcollection'
            plugin_entry = link.create_group(group_name)
            plugin_entry.attrs[NX_CLASS] = 'NXdata'
        else:
            raise Exception("The link type is not known")

        self.__output_metadata(data, plugin_entry)
        self._barrier()

    def __output_metadata(self, data, entry):
        self.__output_axis_labels(data, entry)
        self.__output_data_patterns(data, entry)
        self.__output_metadata_dict(data, entry)

    def __output_axis_labels(self, data, entry):
        self._barrier()

        axis_labels = data.data_info.get("axis_labels")
        axes = []
        count = 0
        for labels in axis_labels:
            name = labels.keys()[0]
            axes.append(name)
            entry.attrs[name + '_indices'] = count

            try:
                mData = data.meta_data.get(name)
            except KeyError:
                mData = np.arange(data.get_shape()[count])

            if isinstance(mData, list):
                mData = np.array(mData)

            axis_entry = entry.create_dataset(name, mData.shape, mData.dtype)
            axis_entry[...] = mData[...]
            axis_entry.attrs['units'] = labels.values()[0]
            count += 1
        entry.attrs['axes'] = axes
        self._barrier()

    def __output_data_patterns(self, data, entry):
        self._barrier()
        logging.debug("Outputting data patterns to file")

        data_patterns = data.data_info.get("data_patterns")
        entry = entry.create_group('patterns')
        entry.attrs[NX_CLASS] = 'NXcollection'
        for pattern in data_patterns:
            nx_data = entry.create_group(pattern)
            nx_data.attrs[NX_CLASS] = 'NXparameters'
            values = data_patterns[pattern]
            nx_data.create_dataset('core_dir', data=values['core_dir'])
            nx_data.create_dataset('slice_dir', data=values['slice_dir'])

        self._barrier()

    def __output_metadata_dict(self, data, entry):
        self._barrier()
        logging.debug("Outputting meta data dictionary to file")

        meta_data = data.meta_data.get_dictionary()
        entry = entry.create_group('meta_data')
        entry.attrs[NX_CLASS] = 'NXcollection'
        for mData in meta_data:
            nx_data = entry.create_group(mData)
            nx_data.attrs[NX_CLASS] = 'NXdata'
            nx_data.create_dataset(mData, data=meta_data[mData])

        self._barrier()
