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
import textwrap

import numpy as np
from colorama import Fore, Back, Style
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

    def _save_plugin_list(self, out_filename, exp=None):
        import re
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

            if 'cite' in plugin.keys():
                if plugin['cite'] is not None:
                    self._output_plugin_citations(plugin['cite'], plugin_group)

#                if plugin['cite'] is not None:
#                citation_group = plugin_group.create_group('citation')
#                    plugin['cite'].write(citation_group)

            count += 1

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
        width = 85
        if verbose == '-q':
            return self.__get_plugin_title(plugin, count, width, quiet=True)
        if not verbose:
            return self.__get_basic(plugin, count, width)
        if verbose == '-v':
            return self.__get_verbose(plugin, count, width)
        if verbose == '-vv':
            return self.__get_verbose_verbose(plugin, count, width)

    def __get_plugin_title(self, plugin, count, width, quiet=False):
        active = \
            '***OFF***' if 'active' in plugin and not plugin['active'] else ''
        pos = plugin['pos'].strip() if 'pos' in plugin.keys() else count
        fore_colour = Fore.RED + Style.DIM if active else Fore.LIGHTWHITE_EX
        title = "%s %2s) %s" % (active, pos, plugin['name'])
        if not quiet:
            title += "(%s)" % plugin['id']
        width -= len(title)
        return Back.LIGHTBLACK_EX + fore_colour + title + " "*width + \
            Style.RESET_ALL

    def __get_basic(self, plugin, count, width):
        title = self.__get_plugin_title(plugin, count, width, quiet=True)
        params = self._get_param_details(plugin['data'], width)
        return title + params

    def __get_verbose(self, plugin, count, width, breakdown=False):
        title = self.__get_plugin_title(plugin, count, width)
        colour_on = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
        colour_off = Back.RESET + Fore.RESET
        synopsis = \
            self._get_synopsis(plugin['name'], width, colour_on, colour_off)
        params = self._get_param_details(
            plugin['data'], width, desc=plugin['desc'])
        if breakdown:
            return title, synopsis, params
        return title + synopsis + params

    def __get_verbose_verbose(self, plugin, count, width):
        title, synopsis, param_details = \
            self.__get_verbose(plugin, count, width, breakdown=True)
        extra_info = self._get_docstring_info(plugin['name'])
        info_colour = Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
        warn_colour = Back.RED + Fore.WHITE
        colour_off = Back.RESET + Fore.RESET
        info = self._get_equal_lines(extra_info['info'], width,
                                     info_colour, colour_off, " "*4)
        warn = self._get_equal_lines(extra_info['warn'], width,
                                     warn_colour, colour_off, " "*4)
        info = "\n"+info if info else ''
        warn = "\n"+warn if warn else ''
        return title + synopsis + info + warn + param_details

    def _get_synopsis(self, plugin_name, width, colour_on, colour_off):
        synopsis = self._get_equal_lines(self._get_docstring_info(
            plugin_name)['synopsis'], width, colour_on, colour_off, " "*2)
        if not synopsis:
            return ''
        return "\n" + colour_on + synopsis + colour_off

    def _get_param_details(self, pdata, width, desc=False):
        margin = 4
        keycount = 0
        joiner = "\n" + " "*margin
        params = ''
        for key in pdata.keys():
            keycount += 1
            temp = "\n   %2i)   %20s : %s"
            params += temp % (keycount, key, pdata[key])
            if desc:
                pdesc = " ".join(desc[key].split())
                pdesc = joiner.join(textwrap.wrap(pdesc, width=width))
                temp = '\n' + Fore.CYAN + ' '*margin + "%s" + Fore.RESET
                params += temp % pdesc
        return params

    def _get_equal_lines(self, string, width, colour_on, colour_off, offset):
        if not string:
            return ''
        str_list = textwrap.wrap(string, width=width-len(offset))
        new_str_list = []
        for line in str_list:
            lwidth = width - len(line) - len(offset)
            new_str_list.append(
                colour_on + offset + line + " "*lwidth + colour_off)
        return "\n".join(new_str_list)

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

    def __get_loaders_and_savers_index(self):
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
