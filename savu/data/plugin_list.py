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
   :synopsis: Contains the PluginList class, which deals with loading and \
   saving the plugin list, and the CitationInformation class. An instance is \
   held by the MetaData class.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import h5py
import json
import copy
import inspect
import re

import numpy as np
import savu.plugins.utils as pu
import savu.data.framework_citations as fc


NX_CLASS = 'NX_class'


class PluginList(object):
    """
    The PluginList class handles the plugin list - loading, saving and adding
    citation information for the plugin
    """

    def __init__(self):
        self.plugin_list = []
        self.n_plugins = None
        self.n_loaders = 0
        self.n_savers = 0
        self.loader_idx = None
        self.saver_idx = None
        self.datasets_list = []
        self.saver_plugin_status = True

    def _get_plugin_entry_template(self):
        template = {'active': True,
                    'name': None,
                    'id': None,
                    'desc': None,
                    'data': None,
                    'user': [],
                    'hide': []}
        return template

    def __get_json_keys(self):
        return ['data', 'desc', 'user', 'hide']

    def _populate_plugin_list(self, filename, activePass=False):
        """ Populate the plugin list from a nexus file. """

        plugin_file = h5py.File(filename, 'r')
        plugin_group = plugin_file['entry/plugin']
        self.plugin_list = []
        single_val = ['name', 'id', 'pos', 'active']
        for key in plugin_group.keys():
            plugin = self._get_plugin_entry_template()
            entry_keys = plugin_group[key].keys()
            json_keys = [k for k in entry_keys if k not in single_val]

            if 'active' in entry_keys:
                plugin['active'] = plugin_group[key]['active'][0]

            if plugin['active'] or activePass:
                plugin['name'] = plugin_group[key]['name'][0]
                plugin['id'] = plugin_group[key]['id'][0]
                plugin['pos'] = key.encode('ascii').strip()

                for jkey in json_keys:
                    plugin[jkey] = self.__convert_to_list(self.__byteify(
                        json.loads(plugin_group[key][jkey][0])))
                self.plugin_list.append(plugin)
        plugin_file.close()

    def _save_plugin_list(self, out_filename, exp=None):
        if exp:
            entry_group = exp.nxs_file.create_group('entry')
        else:
            plugin_file = h5py.File(out_filename, 'w')
            entry_group = plugin_file.create_group('entry')

        entry_group.attrs[NX_CLASS] = 'NXentry'
        citations_group = entry_group.create_group('framework_citations')
        citations_group.attrs[NX_CLASS] = 'NXcollection'
        self._save_framework_citations(citations_group)
        plugins_group = entry_group.create_group('plugin')
        plugins_group.attrs[NX_CLASS] = 'NXprocess'

        count = 1
        for plugin in self.plugin_list:
            self.__populate_plugins_group(plugins_group, plugin, count)
            count += 1

    def __populate_plugins_group(self, plugins_group, plugin, count):
        import re
        if 'pos' in plugin.keys():
            num = int(re.findall('\d+', plugin['pos'])[0])
            letter = re.findall('[a-z]', plugin['pos'])
            letter = letter[0] if letter else ""
            plugin_group = \
                plugins_group.create_group("%*i%*s" % (4, num, 1, letter))
        else:
            plugin_group = plugins_group.create_group("%*i" % (4, count))

        plugin_group.attrs[NX_CLASS] = 'NXnote'

        required_keys = self._get_plugin_entry_template().keys()
        json_keys = self.__get_json_keys()

        if 'cite' in plugin.keys():
            if plugin['cite'] is not None:
                self._output_plugin_citations(plugin['cite'], plugin_group)

        for key in required_keys:
            array = np.array([json.dumps(plugin[key])]) if key in json_keys \
                else np.array([plugin[key]])
            plugin_group.create_dataset(key, array.shape, array.dtype, array)

    def _add(self, idx, entry):
        self.plugin_list.insert(idx, entry)
        self.__set_loaders_and_savers()

    def _remove(self, idx):
        del self.plugin_list[idx]
        self.__set_loaders_and_savers()

    def _output_plugin_citations(self, citations, group):
        if not isinstance(citations, list):
            citations = [citations]
        for cite in citations:
            citation_group = group.create_group(cite.name)
            cite.write(citation_group)

    def _save_framework_citations(self, group):
        framework_cites = fc.get_framework_citations()
        count = 0
        for cite in framework_cites:
            citation_group = group.create_group(cite['name'])
            citation = CitationInformation()
            del cite['name']
            for key, value in cite.iteritems():
                exec('citation.' + key + '= value')
            citation.write(citation_group)
            count += 1

    def _get_docstring_info(self, plugin):
        plugin_inst = pu.plugins[plugin]()
        plugin_inst._populate_default_parameters()
        return plugin_inst.docstring_info

    def __byteify(self, input):
        if isinstance(input, dict):
            return {self.__byteify(key): self.__byteify(value)
                    for key, value in input.iteritems()}
        elif isinstance(input, list):
            temp = [self.__byteify(element) for element in input]
            return temp
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    def __convert_to_list(self, data):
        if isinstance(data, list):
            return data
        for key in data:
            value = data[key]
            if isinstance(value, str) and value.count('['):
                value = \
                    [[a.split(']')[0].split('[')[1]] for a in value.split(';')]
                value = [v[0].split(',') for v in value]
                new_str = str(value[0])
                if len(value) > 1:
                    value = [new_str+';'+str(b) for b in value[1:]][0]
                else:
                    value = new_str
                exec("value =" + value)
            data[key] = value
        return data

    def _set_datasets_list(self, plugin):
        in_pData, out_pData = plugin.get_plugin_datasets()
        max_frames = plugin.get_max_frames()
        in_data_list = self._populate_datasets_list(in_pData, max_frames)
        out_data_list = self._populate_datasets_list(out_pData, max_frames)
        self.datasets_list.append({'in_datasets': in_data_list,
                                   'out_datasets': out_data_list})

    def _populate_datasets_list(self, data, max_frames):
        data_list = []
        for d in data:
            name = d.data_obj.get_name()
            pattern = copy.deepcopy(d.get_pattern())
            pattern[pattern.keys()[0]]['max_frames'] = max_frames
            data_list.append({'name': name, 'pattern': pattern})
        return data_list

    def _get_datasets_list(self):
        return self.datasets_list

    def _reset_datsets_list(self):
        self.datasets_list = []

    def _get_n_loaders(self):
        return self.n_loaders

    def _get_n_savers(self):
        return self.n_savers

    def _get_loaders_index(self):
        return self.loader_idx

    def _get_savers_index(self):
        return self.saver_idx

    def _get_n_processing_plugins(self):
        return len(self.plugin_list) - self._get_n_loaders()

    def __set_loaders_and_savers(self):
        """ Get lists of loader and saver positions within the plugin list and
        set the number of loaders.

        :returns: loader index list and saver index list
        :rtype: list(int(loader)), list(int(saver))
        """
        from savu.plugins.loaders.base_loader import BaseLoader
        from savu.plugins.savers.base_saver import BaseSaver
        loader_idx = []
        saver_idx = []
        self.n_plugins = len(self.plugin_list)

        for i in range(self.n_plugins):
            bases = inspect.getmro(pu.load_class(self.plugin_list[i]['id']))
            loader_list = [b for b in bases if b == BaseLoader]
            saver_list = [b for b in bases if b == BaseSaver]
            if loader_list:
                loader_idx.append(i)
            if saver_list:
                saver_idx.append(i)
        self.loader_idx = loader_idx
        self.saver_idx = saver_idx
        self.n_loaders = len(loader_idx)
        self.n_savers = len(saver_idx)

    def _check_loaders(self):
        """ Check plugin list starts with a loader and ends with a saver.
        """
        self.__set_loaders_and_savers()
        loaders = self._get_loaders_index()

        if loaders:
            if loaders[0] is not 0 or loaders[-1]+1 is not len(loaders):
                raise Exception("All loader plugins must be at the beginning "
                                "of the plugin list")
        else:
            raise Exception("The first plugin in the plugin list must be a "
                            "loader plugin.")

    def _add_missing_savers(self, data_names):
        """ Add savers for missing datasets. """
        saved_data = []
        for i in self._get_savers_index():
            saved_data.append(self.plugin_list[i]['data']['in_datasets'])
        saved_data = set([s for sub_list in saved_data for s in sub_list])

        for name in [data for data in data_names if data not in saved_data]:
            process = {}
            pos = int(re.search(r'\d+', self.plugin_list[-1]['pos']).group())+1
            plugin = pu.get_plugin('savu.plugins.savers.hdf5_saver')
            plugin.parameters['in_datasets'] = [name]
            process['name'] = plugin.name
            process['id'] = plugin.__module__
            process['pos'] = str(pos)
            process['data'] = plugin.parameters
            process['active'] = True
            process['desc'] = plugin.parameters_desc
            self._add(pos, process)

    def _get_dataset_flow(self):
        datasets_idx = []
        n_loaders = self._get_n_loaders()
        n_plugins = self._get_n_processing_plugins()
        for i in range(self.n_loaders, n_loaders+n_plugins):
            datasets_idx.append(self.plugin_list[i]['data']['out_datasets'])
        return datasets_idx

    def _contains_gpu_processes(self):
        """ Returns True if gpu processes exist in the process list. """
        from savu.plugins.driver.gpu_plugin import GpuPlugin
        for i in range(self.n_plugins):
            bases = inspect.getmro(pu.load_class(self.plugin_list[i]['id']))
            if GpuPlugin in bases:
                return True
        return False


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
        self.name = 'citation'

    def write(self, citation_group):
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

