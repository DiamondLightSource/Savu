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
import ast
import copy
import inspect
import json
import logging
import os
import re
from collections import defaultdict

import h5py
import numpy as np

import savu.data.framework_citations as fc
import savu.plugins.docstring_parser as doc
import savu.plugins.loaders.utils.yaml_utils as yu
import savu.plugins.utils as pu
from savu.data.meta_data import MetaData

NX_CLASS = "NX_class"


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
        self._template = None
        self.version = None
        self.iterate_plugin_groups = []

    def add_template(self, create=False):
        self._template = Template(self)
        if create:
            self._template.creating = True

    def _get_plugin_entry_template(self):
        template = {"active": True, "name": None, "id": None, "data": None}
        return template

    def __get_json_keys(self):
        return ["data"]

    def _populate_plugin_list(
        self, filename, active_pass=False, template=False
    ):
        """ Populate the plugin list from a nexus file. """
        with h5py.File(filename, "r") as plugin_file:
            if "entry/savu_notes/version" in plugin_file:
                self.version = plugin_file["entry/savu_notes/version"][()]
                self._show_process_list_version()

            plugin_group = plugin_file["entry/plugin"]
            self.plugin_list = []
            single_val = ["name", "id", "pos", "active"]
            exclude = ["citation"]
            ordered_pl_keys = pu.sort_alphanum(list(plugin_group.keys()))
            for group in ordered_pl_keys:
                plugin = self._get_plugin_entry_template()
                entry_keys = plugin_group[group].keys()
                parameters = [
                    k
                    for k in entry_keys
                    for e in exclude
                    if k not in single_val and e not in k
                ]

                if "active" in entry_keys:
                    plugin["active"] = plugin_group[group]["active"][0]

                if plugin['active'] or active_pass:
                    plugin['name'] = plugin_group[group]['name'][0].decode("utf-8")
                    plugin['id'] = plugin_group[group]['id'][0].decode("utf-8")
                    plugin_tools = None
                    try:
                        plugin_class = pu.load_class(plugin["id"])()
                        # Populate the parameters (including those from it's base classes)
                        plugin_tools = plugin_class.get_plugin_tools()
                        if not plugin_tools:
                            raise OSError(f"Tools file not found for {plugin['name']}")
                        plugin_tools._populate_default_parameters()
                    except ImportError:
                        # No plugin class found
                        logging.error(f"No class found for {plugin['name']}")

                    plugin['doc'] = plugin_tools.docstring_info if plugin_tools else ""
                    plugin['tools'] = plugin_tools if plugin_tools else {}
                    plugin['param'] = plugin_tools.get_param_definitions() if \
                        plugin_tools else {}
                    plugin['pos'] = group.strip()

                    for param in parameters:
                        try:
                            plugin[param] = json.loads(plugin_group[group][param][0])
                        except ValueError as e:
                            raise ValueError(
                                f"Error: {e}\n Could not parse key '{param}' from group '{group}' as JSON"
                            )
                    self.plugin_list.append(plugin)

            # add info about groups of plugins to iterate over into
            # self.iterate_plugin_groups
            self.clear_iterate_plugin_group_dicts()
            try:
                iterate_groups = plugin_file['entry/iterate_plugin_groups']
                for key in list(iterate_groups.keys()):
                    iterate_group_dict = {
                        'start_index': iterate_groups[key]['start'][()],
                        'end_index': iterate_groups[key]['end'][()],
                        'iterations': iterate_groups[key]['iterations'][()]
                    }
                    self.iterate_plugin_groups.append(iterate_group_dict)
            except Exception as e:
                err_str = f"Process list file {filename} doesn't have the " \
                          f"iterate_plugin_groups internal hdf5 path"
                print(err_str)

            if template:
                self.add_template()
                self._template.update_process_list(template)

    def _show_process_list_version(self):
        """If the input process list was created using an older version
        of Savu, then alert the user"""
        from savu.version import __version__
        if __version__ != self.version:
            separator = "*" * 53
            print(separator)
            print(f"*** This process list was created using Savu "
                  f"{self.version}  ***")
            print(separator)

    def _save_plugin_list(self, out_filename):
        with h5py.File(out_filename, "a") as nxs_file:

            entry = nxs_file.require_group("entry")

            self._save_framework_citations(self._overwrite_group(
                entry, 'framework_citations', 'NXcollection'))

            self.__save_savu_notes(self._overwrite_group(
                entry, 'savu_notes', 'NXnote'))

            plugins_group = self._overwrite_group(entry, 'plugin', 'NXprocess')

            count = 1
            for plugin in self.plugin_list:
                plugin_group = self._get_plugin_group(
                    plugins_group, plugin, count
                )
                self.__populate_plugins_group(plugin_group, plugin)

            self.__save_iterate_plugin_groups(self._overwrite_group(
                entry, 'iterate_plugin_groups', 'NXnote'))

        if self._template and self._template.creating:
            fname = os.path.splitext(out_filename)[0] + ".savu"
            self._template._output_template(fname, out_filename)

    def _overwrite_group(self, entry, name, nxclass):
        if name in entry:
            entry.pop(name)
        group = entry.create_group(name.encode("ascii"))
        group.attrs[NX_CLASS] = nxclass.encode("ascii")
        return group

    def add_iterate_plugin_group(self, start, end, iterations):
        """Add an element to self.iterate_plugin_groups"""
        group_new = {
            'start_index': start,
            'end_index': end,
            'iterations': iterations
        }

        if iterations <= 0:
            print("The number of iterations should be larger than zero and nonnegative")
            return
        elif start <= 0 or start > len(self.plugin_list) or end <= 0 or end > len(self.plugin_list):
            print("The given plugin indices are not within the range of existing plugin indices")
            return

        are_crosschecks_ok = \
            self._crosscheck_existing_loops(start, end, iterations)

        if are_crosschecks_ok:
            self.iterate_plugin_groups.append(group_new)
            info_str = f"The following loop has been added: start plugin " \
                       f"index {group_new['start_index']}, end plugin index " \
                       f"{group_new['end_index']}, iterations " \
                       f"{group_new['iterations']}"
            print(info_str)

    def _crosscheck_existing_loops(self, start, end, iterations):
        """
        Check requested loop to be added against existing loops for potential
        clashes
        """
        are_crosschecks_ok = False
        list_new_indices = list(range(start, end+1))
        # crosscheck with the existing iterative loops
        if len(self.iterate_plugin_groups) != 0:
            noexactlist = True
            nointersection = True
            for count, group in enumerate(self.iterate_plugin_groups, 1):
                start_int = int(group['start_index'])
                end_int = int(group['end_index'])
                list_existing_indices = list(range(start_int, end_int+1))
                if bool(set(list_new_indices).intersection(list_existing_indices)):
                    # check if the intersection of lists is exact (number of iterations to change)
                    nointersection = False
                    if list_new_indices == list_existing_indices:
                        print(f"The number of iterations of loop group no. {count}, {list_new_indices} has been set to: {iterations}")
                        self.iterate_plugin_groups[count-1]["iterations"] = iterations
                        noexactlist = False
                    else:
                        print(f"The plugins of group no. {count} are already set to be iterative: {set(list_new_indices).intersection(list_existing_indices)}")
            if noexactlist and nointersection:
                are_crosschecks_ok = True
        else:
            are_crosschecks_ok = True

        return are_crosschecks_ok

    def remove_iterate_plugin_groups(self, indices):
        """ Remove elements from self.iterate_plugin_groups """
        if len(indices) == 0:
            # remove all iterative loops in process list
            prompt_str = 'Are you sure you want to remove all iterative ' \
                'loops? [y/N]'
            check = input(prompt_str)
            should_remove_all = check.lower() == 'y'
            if should_remove_all:
                self.clear_iterate_plugin_group_dicts()
                print('All iterative loops have been removed')
            else:
                print('No iterative loops have been removed')
        else:
            # remove specified iterative loops in process list
            sorted_indices = sorted(indices)

            if sorted_indices[0] <= 0:
                print('The iterative loops are indexed starting from 1')
                return

            for i in reversed(sorted_indices):
                try:
                    # convert the one-based index to a zero-based index
                    iterate_group = self.iterate_plugin_groups.pop(i - 1)
                    info_str = f"The following loop has been removed: start " \
                               f"plugin index " \
                               f"{iterate_group['start_index']}, " \
                               f"end plugin index " \
                               f"{iterate_group['end_index']}, iterations " \
                               f"{iterate_group['iterations']}"
                    print(info_str)
                except IndexError as e:
                    info_str = f"There doesn't exist an iterative loop with " \
                               f"number {i}"
                    print(info_str)

    def clear_iterate_plugin_group_dicts(self):
        """
        Reset the list of dicts representing groups of plugins to iterate over
        """
        self.iterate_plugin_groups = []

    def get_iterate_plugin_group_dicts(self):
        """
        Return the list of dicts representing groups of plugins to iterate over
        """
        return self.iterate_plugin_groups

    def print_iterative_loops(self):
        if len(self.iterate_plugin_groups) == 0:
            print('There are no iterative loops in the current process list')
        else:
            print('Iterative loops in the current process list are:')
            for count, group in enumerate(self.iterate_plugin_groups, 1):
                number = f"({count}) "
                start_str = f"start plugin index: {group['start_index']}"
                end_str = f"end index: {group['end_index']}"
                iterations_str = f"iterations number: {group['iterations']}"
                full_str = number + start_str + ', ' + end_str + ', ' + \
                    iterations_str
                print(full_str)

    def remove_associated_iterate_group_dict(self, pos, direction):
        """
        Remove an iterative loop associated to a plugin index
        """
        operation = 'add' if direction == 1 else 'remove'
        for i, iterate_group in enumerate(self.iterate_plugin_groups):
            if operation == 'remove':
                if iterate_group['start_index'] <= pos and \
                    pos <= iterate_group['end_index']:
                    # remove the loop if the plugin being removed is at any
                    # position within an iterative loop
                    del self.iterate_plugin_groups[i]
                    break
            elif operation == 'add':
                if iterate_group['start_index'] != iterate_group['end_index']:
                    # remove the loop only if the plugin is being added between
                    # the start and end of the loop
                    if iterate_group['start_index'] < pos and \
                        pos <= iterate_group['end_index']:
                        del self.iterate_plugin_groups[i]
                        break

    def check_pos_in_iterative_loop(self, pos):
        """
        Check if the given plugin position is in an iterative loop
        """
        is_in_loop = False
        for iterate_group in self.iterate_plugin_groups:
            if iterate_group['start_index'] <= pos and \
                pos <= iterate_group['end_index']:
                is_in_loop = True
                break

        return is_in_loop

    def __save_iterate_plugin_groups(self, group):
        '''
        Save information regarding the groups of plugins to iterate over
        '''
        for count, iterate_group in enumerate(self.iterate_plugin_groups):
            grp_name = str(count)
            grp = group.create_group(grp_name.encode('ascii'))
            shape = () # scalar data
            grp.create_dataset('start'.encode('ascii'), shape, 'i',
                iterate_group['start_index'])
            grp.create_dataset('end'.encode('ascii'), shape, 'i',
                iterate_group['end_index'])
            grp.create_dataset('iterations'.encode('ascii'), shape, 'i',
                iterate_group['iterations'])

    def shift_subsequent_iterative_loops(self, pos, direction):
        """
        Shift all iterative loops occurring after a given plugin position
        """
        # if removing a plugin that is positioned before a loop, the loop should
        # be shifted down by 1; but if removing a plugin that is positioned at
        # the start of the loop, it will be removed instead of shifted (ie, both
        # < or <= work for this case)
        #
        # if adding a plugin that will be positioned before a loop, the loop
        # should be shifted up by 1; also, if adding a plugin to be positioned
        # where the start of a loop currently exists, this should shift the loop
        # up by 1 as well (ie, only <= works for this case, hence the use of <=)
        for iterate_group in self.iterate_plugin_groups:
            if pos <= iterate_group['start_index']:
                self.shift_iterative_loop(iterate_group, direction)

    def shift_range_iterative_loops(self, positions, direction):
        """
        Shift all iterative loops within a range of plugin indices
        """
        for iterate_group in self.iterate_plugin_groups:
            if positions[0] <= iterate_group['start_index'] and \
                iterate_group['end_index'] <= positions[1]:
                self.shift_iterative_loop(iterate_group, direction)

    def shift_iterative_loop(self, iterate_group, direction):
        """
        Shift an iterative loop up or down in the process list, based on if a
        plugin is added or removed
        """
        if direction == 1:
            iterate_group['start_index'] += 1
            iterate_group['end_index'] += 1
        elif direction == -1:
            iterate_group['start_index'] -= 1
            iterate_group['end_index'] -= 1
        else:
            err_str = f"Bad direction value given to shift iterative loop: " \
                      f"{direction}"
            raise ValueError(err_str)

    def __save_savu_notes(self, notes):
        """ Save the version number

        :param notes: hdf5 group to save data to
        """
        from savu.version import __version__

        notes["version"] = __version__

    def __populate_plugins_group(self, plugin_group, plugin):
        """Populate the plugin group information which will be saved

        :param plugin_group: Plugin group to save to
        :param plugin: Plugin to be saved
        """
        plugin_group.attrs[NX_CLASS] = "NXnote".encode("ascii")
        required_keys = self._get_plugin_entry_template().keys()
        json_keys = self.__get_json_keys()

        self._save_citations(plugin, plugin_group)

        for key in required_keys:
            # only need to apply dumps if saving in configurator
            if key == "data":
                data = {}
                for k, v in plugin[key].items():
                    #  Replace any missing quotes around variables.
                    data[k] = pu._dumps(v)
            else:
                data = plugin[key]

            # get the string value
            data = json.dumps(data) if key in json_keys else plugin[key]
            # if the data is string it has to be encoded to ascii so that
            # hdf5 can save out the bytes
            if isinstance(data, str):
                data = data.encode("ascii")
            data = np.array([data])
            plugin_group.create_dataset(
                key.encode("ascii"), data.shape, data.dtype, data
            )

    def _get_plugin_group(self, plugins_group, plugin, count):
        """Return the plugin_group, into which the plugin information
         will be saved

        :param plugins_group: Current group to save inside
        :param plugin: Plugin to be saved
        :param count: Order number of the plugin in the process list
        :return: plugin group
        """
        if "pos" in plugin.keys():
            num = int(re.findall(r"\d+", str(plugin["pos"]))[0])
            letter = re.findall("[a-z]", str(plugin["pos"]))
            letter = letter[0] if letter else ""
            group_name = "%i%s" % (num, letter)
        else:
            group_name = count
        return plugins_group.create_group(group_name.encode("ascii"))

    def _add(self, idx, entry):
        self.plugin_list.insert(idx, entry)
        self.__set_loaders_and_savers()

    def _remove(self, idx):
        del self.plugin_list[idx]
        self.__set_loaders_and_savers()

    def _save_citations(self, plugin, group):
        """Save all the citations in the plugin

        :param plugin: dictionary of plugin information
        :param group: Group to save to
        """
        if "tools" in plugin.keys():
            citation_plugin = plugin.get("tools").get_citations()
            if citation_plugin:
                count = 1
                for citation in citation_plugin.values():
                    group_label = f"citation{count}"
                    if (
                        not citation.dependency
                        or self._dependent_citation_used(plugin, citation)
                    ):
                        self._save_citation_group(
                            citation, citation.__dict__, group, group_label
                        )
                        count += 1

    def _dependent_citation_used(self, plugin, citation):
        """Check if any Plugin parameter values match the citation
        dependency requirement.

        :param plugin: dictionary of plugin information
        :param citation: A plugin citation
        :return: bool True if the citation is for a parameter value
            being used inside this plugin
        """
        parameters = plugin["data"]
        for (
            citation_dependent_parameter,
            citation_dependent_value,
        ) in citation.dependency.items():
            current_value = parameters[citation_dependent_parameter]
            if current_value == citation_dependent_value:
                return True
        return False

    def _exec_citations(self, cite, citation):
        """Execute citations to variable
        :param cite: citation dictionary
        """
        for key, value in cite.items():
            exec("citation." + key + "= value")

    def _save_framework_citations(self, group):
        """Save all the citations in dict

        :param group: Group for nxs file
        """
        framework_cites = fc.get_framework_citations()
        for cite in framework_cites.values():
            label = cite.short_name_article
            del cite.short_name_article
            self._save_citation_group(cite, cite.__dict__, group, label)


    def _save_citation_group(self, citation, cite_dict, group, group_label):
        """Save the citations to the provided group label

        :param citation: Citation object
        :param cite_dict: Citation dictionary
        :param group: Group
        :param group_label: Group label
        :return:
        """
        citation_group = group.require_group(group_label.encode("ascii"))
        self._exec_citations(cite_dict, citation)
        citation.write(citation_group)

    def _get_docstring_info(self, plugin):
        plugin_inst = pu.plugins[plugin]()
        tools = plugin_inst.get_plugin_tools()
        tools._populate_default_parameters()
        return plugin_inst.docstring_info

    # def _byteify(self, input):
    #     if isinstance(input, dict):
    #         return {self._byteify(key): self._byteify(value)
    #                 for key, value in input.items()}
    #     elif isinstance(input, list):
    #         temp = [self._byteify(element) for element in input]
    #         return temp
    #     elif isinstance(input, str):
    #         return input.encode('utf-8')
    #     else:
    #         return input

    def _set_datasets_list(self, plugin):
        in_pData, out_pData = plugin.get_plugin_datasets()
        in_data_list = self._populate_datasets_list(in_pData)
        out_data_list = self._populate_datasets_list(out_pData)
        self.datasets_list.append({'in_datasets': in_data_list,
                                   'out_datasets': out_data_list})

    def _populate_datasets_list(self, data):
        data_list = []
        for d in data:
            name = d.data_obj.get_name()
            pattern = copy.deepcopy(d.get_pattern())
            pattern[list(pattern.keys())[0]]['max_frames_transfer'] = \
                d.meta_data.get('max_frames_transfer')
            pattern[list(pattern.keys())[0]]['transfer_shape'] = \
                d.meta_data.get('transfer_shape')
            data_list.append({'name': name, 'pattern': pattern})
        return data_list

    def _get_datasets_list(self):
        return self.datasets_list

    def _reset_datasets_list(self):
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
        """Get lists of loader and saver positions within the plugin list and
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
            pid = self.plugin_list[i]["id"]
            bases = inspect.getmro(pu.load_class(pid))
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
        """Check plugin list starts with a loader."""
        self.__set_loaders_and_savers()
        loaders = self._get_loaders_index()

        if loaders:
            if loaders[0] != 0 or loaders[-1] + 1 != len(loaders):
                raise Exception("All loader plugins must be at the beginning "
                                "of the process list")
        else:
            raise Exception("The first plugin in the process list must be a "
                            "loader plugin.")

    def _add_missing_savers(self, exp):
        """ Add savers for missing datasets. """
        data_names = exp.index["in_data"].keys()
        saved_data = []

        for i in self._get_savers_index():
            saved_data.append(self.plugin_list[i]["data"]["in_datasets"])
        saved_data = set([s for sub_list in saved_data for s in sub_list])

        for name in [data for data in data_names if data not in saved_data]:
            pos = exp.meta_data.get("nPlugin") + 1
            exp.meta_data.set("nPlugin", pos)
            process = {}
            plugin = pu.load_class("savu.plugins.savers.hdf5_saver")()
            ptools = plugin.get_plugin_tools()
            plugin.parameters["in_datasets"] = [name]
            process["name"] = plugin.name
            process["id"] = plugin.__module__
            process["pos"] = str(pos + 1)
            process["data"] = plugin.parameters
            process["active"] = True
            process["param"] = ptools.get_param_definitions()
            process["doc"] = ptools.docstring_info
            process["tools"] = ptools
            self._add(pos + 1, process)

    def _update_datasets(self, plugin_no, data_dict):
        n_loaders = self._get_n_loaders()
        idx = self._get_n_loaders() + plugin_no
        self.plugin_list[idx]["data"].update(data_dict)

    def _get_dataset_flow(self):
        datasets_idx = []
        n_loaders = self._get_n_loaders()
        n_plugins = self._get_n_processing_plugins()
        for i in range(self.n_loaders, n_loaders + n_plugins):
            datasets_idx.append(self.plugin_list[i]["data"]["out_datasets"])
        return datasets_idx

    def _contains_gpu_processes(self):
        """ Returns True if gpu processes exist in the process list. """
        try:
            from savu.plugins.driver.gpu_plugin import GpuPlugin

            for i in range(self.n_plugins):
                bases = inspect.getmro(
                    pu.load_class(self.plugin_list[i]["id"])
                )
                if GpuPlugin in bases:
                    return True
        except ImportError as ex:
            if "pynvml" in ex.message:
                logging.error(
                    "Error while importing GPU dependencies: %s", ex.message
                )
            else:
                raise

        return False


class Template(object):
    """A class to read and write templates for plugin lists."""

    def __init__(self, plist):
        super(Template, self).__init__()
        self.plist = plist
        self.creating = False

    def _output_template(self, fname, process_fname):
        plist = self.plist.plugin_list
        index = [i for i in range(len(plist)) if plist[i]["active"]]

        local_dict = MetaData(ordered=True)
        global_dict = MetaData(ordered=True)
        local_dict.set(["process_list"], os.path.abspath(process_fname))

        for i in index:
            params = self.__get_template_params(plist[i]["data"], [])
            name = plist[i]["name"]
            for p in params:
                ptype, isyaml, key, value = p
                if isyaml:
                    data_name = isyaml if ptype == "local" else "all"
                    local_dict.set([i + 1, name, data_name, key], value)
                elif ptype == "local":
                    local_dict.set([i + 1, name, key], value)
                else:
                    global_dict.set(["all", name, key], value)

        with open(fname, "w") as stream:
            local_dict.get_dictionary().update(global_dict.get_dictionary())
            yu.dump_yaml(local_dict.get_dictionary(), stream)

    def __get_template_params(self, params, tlist, yaml=False):
        for key, value in params.items():
            if key == "yaml_file":
                yaml_dict = self._get_yaml_dict(value)
                for entry in list(yaml_dict.keys()):
                    self.__get_template_params(
                        yaml_dict[entry]["params"], tlist, yaml=entry
                    )
            value = pu.is_template_param(value)
            if value is not False:
                ptype, value = value
                isyaml = yaml if yaml else False
                tlist.append([ptype, isyaml, key, value])
        return tlist

    def _get_yaml_dict(self, yfile):
        from savu.plugins.loaders.yaml_converter import YamlConverter

        yaml_c = YamlConverter()
        template_check = pu.is_template_param(yfile)
        yfile = template_check[1] if template_check is not False else yfile
        yaml_c.parameters = {"yaml_file": yfile}
        return yaml_c.setup(template=True)

    def update_process_list(self, template):
        tdict = yu.read_yaml(template)
        del tdict["process_list"]

        for plugin_no, entry in tdict.items():
            plugin = list(entry.keys())[0]
            for key, value in list(entry.values())[0].items():
                depth = self.dict_depth(value)
                if depth == 1:
                    self._set_param_for_template_loader_plugin(
                        plugin_no, key, value
                    )
                elif depth == 0:
                    if plugin_no == "all":
                        self._set_param_for_all_instances_of_a_plugin(
                            plugin, key, value
                        )
                    else:
                        data = self._get_plugin_data_dict(str(plugin_no))
                        data[key] = value
                else:
                    raise Exception("Template key not recognised.")

    def dict_depth(self, d, depth=0):
        if not isinstance(d, dict) or not d:
            return depth
        return max(self.dict_depth(v, depth + 1) for k, v in d.items())

    def _set_param_for_all_instances_of_a_plugin(self, plugin, param, value):
        # find all plugins with this name and replace the param
        for p in self.plist.plugin_list:
            if p["name"] == plugin:
                p["data"][param] = value

    def _set_param_for_template_loader_plugin(self, plugin_no, data, value):
        param_key = list(value.keys())[0]
        param_val = list(value.values())[0]
        pdict = self._get_plugin_data_dict(str(plugin_no))["template_param"]
        pdict = defaultdict(dict) if not pdict else pdict
        pdict[data][param_key] = param_val

    def _get_plugin_data_dict(self, plugin_no):
        """ input plugin_no as a string """
        plist = self.plist.plugin_list
        index = [plist[i]["pos"] for i in range(len(plist))]
        return plist[index.index(plugin_no)]["data"]


class CitationInformation(object):
    """
    Descriptor of Citation Information for plugins
    """

    def __init__(
        self,
        description,
        bibtex="",
        endnote="",
        doi="",
        short_name_article="",
        dependency="",
    ):
        self.description = description
        self.short_name_article = short_name_article
        self.bibtex = bibtex
        self.endnote = endnote
        self.doi = doi
        self.dependency = dependency
        self.name = self._set_citation_name()
        self.id = self._set_id()

    def _set_citation_name(self):
        """Create a short identifier using the short name of the article
        and the first author
        """
        cite_info = True if self.endnote or self.bibtex else False

        if cite_info and self.short_name_article:
            cite_name = (
                self.short_name_article.title()
                + " by "
                + self._get_first_author()
                + " et al."
            )
        elif cite_info:
            cite_name = (
                self._get_title()
                + " by "
                + self._get_first_author()
                + " et al."
            )
        else:
            # Set the tools class name as the citation name causes overwriting
            # module_name = tool_class.__module__.split('.')[-1].replace('_', ' ')
            # cite_name = module_name.split('tools')[0].title()
            cite_name = self.description
        return cite_name

    def _set_citation_id(self, tool_class):
        """Create a short identifier using the bibtex identification"""
        # Remove blank space
        if self.bibtex:
            cite_id = self._get_id()
        else:
            # Set the tools class name as the citation name
            module_name = tool_class.__module__.split(".")[-1]
            cite_id = module_name
        return cite_id

    def _set_id(self):
        """ Retrieve the id from the bibtex """
        cite_id = self.seperate_bibtex("@article{", ",")
        return cite_id

    def _get_first_author(self):
        """ Retrieve the first author name """
        if self.endnote:
            first_author = self.seperate_endnote("%A ")
        elif self.bibtex:
            first_author = self.seperate_bibtex("author={", "}", author=True)
        return first_author

    def _get_title(self):
        """ Retrieve the title """
        if self.endnote:
            title = self.seperate_endnote("%T ")
        elif self.bibtex:
            title = self.seperate_bibtex("title={", "}")
        return title

    def seperate_endnote(self, seperation_char):
        """Return the string contained between start characters
        and a new line

        :param seperation_char: Character to split the string at
        :return: The string contained between start characters and a new line
        """
        item = self.endnote.partition(seperation_char)[2].split("\n")[0]
        return item

    def seperate_bibtex(self, start_char, end_char, author=False):
        """Return the string contained between provided characters

        :param start_char: Character to split the string at
        :param end_char: Character to end the split at
        :return: The string contained between both characters
        """
        plain_text = doc.remove_new_lines(self.bibtex)
        item = plain_text.partition(start_char)[2].split(end_char)[0]
        if author:
            # Return one author only
            if " and " in item:
                item = item.split(" and ")[0]

        return item

    def write(self, citation_group):
        # classes don't have to be encoded to ASCII
        citation_group.attrs[NX_CLASS] = "NXcite"
        # Valid ascii sequences will be encoded, invalid ones will be
        # preserved as escape sequences
        description_array = np.array([self.description.encode('ascii','backslashreplace')])
        citation_group.create_dataset('description'.encode('ascii'),
                                      description_array.shape,
                                      description_array.dtype,
                                      description_array)
        doi_array = np.array([self.doi.encode('ascii')])
        citation_group.create_dataset('doi'.encode('ascii'),
                                      doi_array.shape,
                                      doi_array.dtype,
                                      doi_array)
        endnote_array = np.array([self.endnote.encode('ascii','backslashreplace')])
        citation_group.create_dataset('endnote'.encode('ascii'),
                                      endnote_array.shape,
                                      endnote_array.dtype,
                                      endnote_array)
        bibtex_array = np.array([self.bibtex.encode('ascii','backslashreplace')])
        citation_group.create_dataset('bibtex'.encode('ascii'),
                                      bibtex_array.shape,
                                      bibtex_array.dtype,
                                      bibtex_array)
