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
.. module:: plugin_list
   :platform: Unix
   :synopsis: Contains the PluginList class, which deals with loading and 
   saving the plugin list, and the CitationInformation class. An instance is 
   held by the MetaData class.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import h5py
import json
import os
import logging

import numpy as np

NX_CLASS = 'NX_class'


class PluginList(object):
    """
    The PluginList class handles the plugin list - loading, saving and adding
    citation information for the plugin
    """

    def __init__(self):
        self.plugin_list = []

    def populate_plugin_list(self, filename):
        plugin_file = h5py.File(filename, 'r')
        plugin_group = plugin_file['entry/plugin']
        self.plugin_list = []
        for key in plugin_group.keys():
	    plugin = {}
            plugin['name'] = plugin_group[key]['name'][0]
            plugin['id'] = plugin_group[key]['id'][0]
            plugin['data'] = json.loads(plugin_group[key]['data'][0])
	    self.plugin_list.append(plugin)
        plugin_file.close()

    def save_plugin_list(self, out_filename):
        plugin_file = h5py.File(out_filename, 'w')
        entry_group = plugin_file.create_group('entry')
        entry_group.attrs[NX_CLASS] = 'NXentry'
        plugins_group = entry_group.create_group('plugin')
        plugins_group.attrs[NX_CLASS] = 'NXplugin'
        count = 0
        for plugin in self.plugin_list:
            plugin_group = plugins_group.create_group("%i" % count)
            plugin_group.attrs[NX_CLASS] = 'NXnote'
            id_array = np.array([plugin['id']])
            plugin_group.create_dataset('id', id_array.shape, id_array.dtype,
                                         id_array)
            name_array = np.array([plugin['name']])
            plugin_group.create_dataset('name', name_array.shape,
                                         name_array.dtype, name_array)
            data_array = np.array([json.dumps(plugin['data'])])
            plugin_group.create_dataset('data', data_array.shape,
                                         data_array.dtype, data_array)
            count += 1
        plugin_file.close()

    def add_plugin_citation(self, filename, plugin_number, citation):
        logging.debug("Adding Citation to file %s", filename)
        plugin_file = h5py.File(filename, 'a')
        plugin_entry = plugin_file['entry/process/%i' % plugin_number]
        citation.write(plugin_entry)
        plugin_file.close()

    def add_intermediate_data_link(self, filename, output_data, group_name):
        logging.debug("Adding link to file %s", filename)
        plugin_file = h5py.File(filename, 'a')
        inter_entry = plugin_file['entry'].require_group('intermediate')
        inter_entry.attrs[NX_CLASS] = 'NXcollection'
        inter_entry[group_name] = output_data.external_link()
        plugin_file.close()

    def get_string(self):
        out_string = []
        count = 0
        for plugin in self.plugin_list:
            count += 1
            description = "%2i) %s(%s)" % (count, plugin['name'], plugin['id'])
            for key in plugin['data'].keys():
                description += "\n     %20s : %s" % (key, plugin['data'][key])
            out_string.append(description)
        return '\n'.join(out_string)


class CitationInformation(object):
    """
    Descriptor of Citation Information for plugins
    """

    def __init__(self):
        super(CitationInformation, self).__init__()
        self.description = "Default Description"
        self.doi = "Default DOI"
        self.endnote = "Default Endnote"
        self.bibtex = "Default Bibtex"

    def write(self, hdf_group):
        citation_group = hdf_group.create_group('citation')
        citation_group.attrs[NX_CLASS] = 'NXcite'
        description_array = np.array([self.description])
        citation_group.create_dataset('description',
                                      description_array.shape,
                                      description_array.dtype,
                                      description_array)
        doi_array = np.array([self.doi])
        citation_group.create_dataset('doi',
                                      doi_array.shape,
                                      doi_array.dtype,
                                      doi_array)
        endnote_array = np.array([self.endnote])
        citation_group.create_dataset('endnote',
                                      endnote_array.shape,
                                      endnote_array.dtype,
                                      endnote_array)
        bibtex_array = np.array([self.bibtex])
        citation_group.create_dataset('bibtex',
                                      bibtex_array.shape,
                                      bibtex_array.dtype,
                                      bibtex_array)
