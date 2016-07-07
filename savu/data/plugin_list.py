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
import logging
import copy
import inspect

import numpy as np

import savu.plugins.utils as pu


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
        self.datasets_list = []
        self.exp = None

    def _populate_plugin_list(self, filename, activePass=False):
        plugin_file = h5py.File(filename, 'r')
        plugin_group = plugin_file['entry/plugin']
        self.plugin_list = []
        for key in plugin_group.keys():
            plugin = {}
            try:
                active = plugin_group[key]['active'][0]
                plugin['active'] = active
                if activePass:
                    active = True
            except KeyError:
                active = True

            if active:
                plugin['name'] = plugin_group[key]['name'][0]
                plugin['id'] = plugin_group[key]['id'][0]
                plugin['pos'] = key.encode('ascii').strip()
                if 'desc' in plugin_group[key].keys():
                    plugin['desc'] = self.__byteify(
                        json.loads(plugin_group[key]['desc'][0]))
                    plugin['desc'] = self.__convert_to_list(plugin['desc'])
                plugin['data'] = \
                    self.__byteify(json.loads(plugin_group[key]['data'][0]))
                plugin['data'] = self.__convert_to_list(plugin['data'])
                self.plugin_list.append(plugin)

        plugin_file.close()

    def _save_plugin_list(self, saver):
        import re
        entry_group = saver.nxs_file.create_group('entry')
        entry_group.attrs[NX_CLASS] = 'NXentry'
        plugins_group = entry_group.create_group('plugin')
        plugins_group.attrs[NX_CLASS] = 'NXplugin'
        count = 1

        for plugin in self.plugin_list:
            if 'pos' in plugin.keys():
                num = int(re.findall('\d+', plugin['pos'])[0])
                letter = re.findall('[a-z]', plugin['pos'])
                letter = letter[0] if letter else ""
                plugin_group = \
                    plugins_group.create_group("%*i%*s" % (4, num, 1, letter))
            else:
                plugin_group = plugins_group.create_group("%*i" % (4, count))

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
            try:
                active_array = np.array([plugin['active']])
                plugin_group.create_dataset('active', active_array.shape,
                                            active_array.dtype, active_array)
            except KeyError:
                pass

            try:
                desc_array = np.array([json.dumps(plugin['desc'])])
                plugin_group.create_dataset('desc', desc_array.shape,
                                            desc_array.dtype, desc_array)
            except KeyError:
                pass

            count += 1

    def add_plugin_citation(self, filename, plugin_number, citation):
        logging.debug("Adding Citation to file %s", filename)
        plugin_file = h5py.File(filename, 'a')
        plugin_entry = plugin_file['entry/process/%i' % plugin_number]
        citation.write(plugin_entry)
        plugin_file.close()

    def _get_string(self, **kwargs):
        out_string = []
        verbosity = kwargs.get('verbose', False)

        start = kwargs.get('start', 0)
        stop = kwargs.get('stop', len(self.plugin_list))
        if stop == -1:
            stop = len(self.plugin_list)

        count = start
        plugin_list = self.plugin_list[start:stop]
        for plugin in plugin_list:
            count += 1
            description = \
                self.__get_description(plugin, count, verbosity)
            out_string.append(description)
        return '\n'.join(out_string)

    def __get_description(self, plugin, count, verbose):
        description = ""
        if 'active' in plugin:
            if not plugin['active']:
                description += "***OFF***"
        pos = plugin['pos'].strip() if 'pos' in plugin.keys() else count
        description += "%2s) %s(%s)" % (pos, plugin['name'], plugin['id'])

        if verbose != '-q':
            keycount = 0
            for key in plugin['data'].keys():
                keycount += 1
                description += "\n  %2i)   %20s : %s" % \
                    (keycount, key, plugin['data'][key])
                if verbose == '-v':
                    desc = plugin['desc'][key].split(' ')
                    desc = ' '.join([desc[i] for i in range(len(desc)) if
                                    desc[i] is not ''])
                    description += "\t\t: %20s" % desc
        return description

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

    def _get_n_loaders(self):
        return self.n_loaders

<<<<<<< .merge_file_qKFpN1
    def _get_n_processing_plugins(self):
        return len(self.plugin_list) - self._get_n_loaders() - 1

    def _get_loaders_and_savers_index(self):
=======
    def __get_loaders_and_savers_index(self):
>>>>>>> .merge_file_MYWWAV
        """ Get lists of loader and saver positions within the plugin list and
        set the number of loaders.

        :returns: loader index list and saver index list
        :rtype: list(int(loader)), list(int(saver))
        """
        from savu.plugins.base_loader import BaseLoader
        from savu.plugins.base_saver import BaseSaver
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

        self.n_loaders = len(loader_idx)
        return loader_idx, saver_idx

    def _check_loaders_and_savers(self):
        """ Check plugin list starts with a loader and ends with a saver.
        """
        loaders, savers = self.__get_loaders_and_savers_index()

        if loaders:
            if loaders[0] is not 0 or loaders[-1]+1 is not len(loaders):
                raise Exception("All loader plugins must be at the beginning "
                                "of the plugin list")
        else:
            raise Exception("The first plugin in the plugin list must be a "
                            "loader.")

        if not savers or savers[0] is not self.n_plugins-1:
            raise Exception("The final plugin in the plugin list must be a "
                            "saver")

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
