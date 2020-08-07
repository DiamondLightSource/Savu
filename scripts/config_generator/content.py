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
.. module:: content
   :platform: Unix
   :synopsis: Content class for the configurator

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from __future__ import print_function, division, absolute_import

import re
import os
import inspect
import scripts.config_generator.mutations as mutations
from colorama import Fore
from collections import OrderedDict

from savu.plugins import utils as pu
from savu.data.plugin_list import PluginList


class Content(object):

    def __init__(self, filename=None, level='basic'):
        self.disp_level = level
        self.plugin_list = PluginList()
        self.plugin_mutations = mutations.plugin_mutations
        self.param_mutations = mutations.param_mutations
        self.filename = filename
        self._finished = False
        self.failed = {}

    def set_finished(self, check='y'):
        self._finished = True if check.lower() == 'y' else False

    def is_finished(self):
        return self._finished

    def fopen(self, infile, update=False, skip=False):
        if os.path.exists(infile):
            self.plugin_list._populate_plugin_list(infile, activePass=True)
        else:
            raise Exception('INPUT ERROR: The file does not exist.')
        self.filename = infile
        if update:
            self.plugin_mutations = self.check_mutations(self.plugin_mutations)
            self.param_mutations = self.check_mutations(self.param_mutations)
            self._apply_plugin_updates(skip)

    def check_mutations(self, mut_dict):
        plist_version = self._version_to_float(self.plugin_list.version)
        for key, subdict in mut_dict.items():
            if 'up_to_version' in subdict.keys():
                up_to_version = self._version_to_float(subdict['up_to_version'])
                if plist_version >= up_to_version:
                    del mut_dict[key]
        return mut_dict

    def _version_to_float(self, version):
        if version == None:
            return 0
        split_vals = version.split('.')
        return float('.'.join([split_vals[0], ''.join(split_vals[1:])]))

    def display(self, formatter, **kwargs):
        if 'level' not in kwargs.keys():
            kwargs['level'] = self.disp_level
        print('\n' + formatter._get_string(**kwargs) + '\n')

    def check_file(self, filename):
        if not filename:
            raise Exception('INPUT ERROR: Please specify the output filepath.')
        path = os.path.dirname(filename)
        path = path if path else '.'
        if not os.path.exists(path):
            file_error = "INPUT_ERROR: Incorrect filepath."
            raise Exception(file_error)

    def save(self, filename, check='y', template=False):
        if check.lower() == 'y':
            print("Saving file %s" % (filename))
            if template:
                self.plugin_list.add_template(create=True)
            self.plugin_list._save_plugin_list(filename)
        else:
            print("The process list has NOT been saved.")

    def clear(self, check='y'):
        if check.lower() == 'y':
            self.plugin_list.plugin_list = []

    def add(self, name, str_pos):
        if name not in pu.plugins.keys():
            if name in self.failed.keys():
                msg = "IMPORT ERROR: %s is unavailable due to the following"\
                " error:\n\t%s" % (name, self.failed[name])
                raise Exception(msg)
            else:
                raise Exception("INPUT ERROR: Unknown plugin %s" % name)
        plugin = pu.plugins[name]()
        plugin._populate_default_parameters()
        pos, str_pos = self.convert_pos(str_pos)
        self.insert(plugin, pos, str_pos)

    def refresh(self, str_pos, defaults=False, change=False):
        pos = self.find_position(str_pos)
        plugin_entry = self.plugin_list.plugin_list[pos]
        name = change if change else plugin_entry['name']
        active = plugin_entry['active']
        plugin = pu.plugins[name]()
        plugin._populate_default_parameters()
        keep = self.get(pos)['data'] if not defaults else None
        self.insert(plugin, pos, str_pos, replace=True)
        self.plugin_list.plugin_list[pos]['active'] = active
        if keep:
            self._update_parameters(plugin, name, keep, str_pos)

    def _update_parameters(self, plugin, name, keep, str_pos):
        union_params = set(keep).intersection(set(plugin.parameters))
        # Names of the parameter names present in both lists
        for param in union_params:
            self.modify(str_pos, param, keep[param], ref=True)
        # add any parameter mutations here
        classes = [c.__name__ for c in inspect.getmro(plugin.__class__)]
        m_dict = self.param_mutations
        keys = [k for k in m_dict.keys() if k in classes]

        changes = False
        for k in keys:
            for entry in m_dict[k]['params']:
                if entry['old'] in keep.keys():
                    changes = True
                    val = keep[entry['old']]
                    if 'eval' in entry.keys():
                        val = eval(entry['eval'])
                    self.modify(str_pos, entry['new'], val, ref=True)
        if changes:
            mutations.param_change_str(keep, plugin.parameters, name, keys)

    def _apply_plugin_updates(self, skip=False):
        # Update old process lists that start from 0
        the_list = self.plugin_list.plugin_list
        if 'pos' in the_list[0].keys() and the_list[0]['pos'] == '0':
            self.increment_positions()

        missing = []
        pos = len(the_list)-1
        notices = mutations.plugin_notices

        for plugin in the_list[::-1]:
            # update old process lists to include 'active' flag
            if 'active' not in plugin.keys():
                plugin['active'] = True

            while(True):
                name = the_list[pos]['name']
                if name in notices.keys():
                    print(notices[name]['desc'])
                # if a plugin is missing then look for mutations
                search = True if name not in pu.plugins.keys() else False
                found = self._mutate_plugins(name, pos, search=search)
                if search and not found:
                    str_pos = self.plugin_list.plugin_list[pos]['pos']
                    missing.append([name, str_pos])
                    self.remove(pos)
                    pos -= 1
                if (name == the_list[pos]['name']):
                    break
            pos -= 1

        exception = False
        for name, pos in missing[::-1]:
            if skip:
                print('Skipping plugin %s: %s' % (pos, name))
            else:
                print("PLUGIN ERROR: The plugin %s is unavailable in this "
                      "version of Savu." % name)
                exception = True
        if exception:
            raise Exception('Incompatible process list.')

    def _mutate_plugins(self, name, pos, search=False):
        """ Perform plugin mutations. """
        # check for case changes in plugin name
        if search:
            for key in pu.plugins.keys():
                if name.lower() == key.lower():
                    str_pos = self.plugin_list.plugin_list[pos]['pos']
                    self.refresh(str_pos, change=key)
                    return True

        # check mutations dict
        m_dict = self.plugin_mutations
        if name in m_dict.keys():
            mutate = m_dict[name]
            if 'replace' in mutate.keys():
                if mutate['replace'] in pu.plugins.keys():
                    str_pos = self.plugin_list.plugin_list[pos]['pos']
                    self.refresh(str_pos, change=mutate['replace'])
                    print(mutate['desc'])
                    return True
                raise Exception('Replacement plugin %s unavailable for %s'
                                % (mutate['replace'], name))
            elif 'remove' in mutate.keys():
                self.remove(pos)
                print(mutate['desc'])
            else:
                raise Exception('Unknown mutation type.')
        return False

    def move(self, old, new):
        old_pos = self.find_position(old)
        entry = self.plugin_list.plugin_list[old_pos]
        self.remove(old_pos)
        new_pos, new = self.convert_pos(new)
        name = entry['name']
        self.insert(pu.plugins[name](), new_pos, new)
        self.plugin_list.plugin_list[new_pos] = entry
        self.plugin_list.plugin_list[new_pos]['pos'] = new

    def modify(self, pos_str, param_name, value, ref=False):
        valid_modification = False
        pos = self.find_position(pos_str)
        tools = self.plugin_list.plugin_list[pos]['tools']
        params = self.plugin_list.plugin_list[pos]['param']
        parameters = self.plugin_list.plugin_list[pos]['data']
        # Select the correct group and order of parameters according to that
        # on display to the user. This ensures correct parameter is modified.

        data_keys = []
        basic_keys = []
        interm_keys = []
        adv_keys = []
        for k, v in params.items():
            if v['display'] == 'on':
                if v['visibility'] == 'datasets':
                    data_keys.append(k)
                if v['visibility'] == 'basic':
                    basic_keys.append(k)
                if v['visibility'] == 'intermediate':
                    interm_keys.append(k)
                if v['visibility'] == 'advanced':
                    adv_keys.append(k)

        keys = basic_keys + interm_keys + adv_keys + data_keys

        if param_name.isdigit():
            param_name = int(param_name)
            if param_name <= len(keys):
                param_name = keys[param_name-1]
            else:
                raise Exception('This parameter number is not valid for this plug in.')
        elif param_name not in keys:
            raise Exception('This parameter is not present in this plug in.')

        try:
            if not ref:
                value = self.value(value)
            valid_modification = tools.modify(parameters, value, param_name)
        except SyntaxError:
            print ("There is a syntax error. Please check your input.")
        except EOFError:
            print ("There is an end of line error. Please check your"
                   " input for the character \"\'\".")
        except Exception as e:
            print(e)
        return valid_modification

    def value(self, value):
        if not value.count(';'):
            try:
                exec("value = " + value)
            except (NameError, SyntaxError):
                exec("value = " + "'" + value + "'")
        return value

    def convert_to_ascii(self, value):
        ascii_list = []
        for v in value:
            ascii_list.append(v.encode('ascii', 'ignore'))
        return ascii_list

    def on_and_off(self, str_pos, index):
        print("switching plugin %s %s" % (str_pos, index))
        status = True if index == 'ON' else False
        pos = self.find_position(str_pos)
        self.plugin_list.plugin_list[pos]['active'] = status

    def convert_pos(self, str_pos):
        """ Converts the display position (input) to the equivalent numerical
        position and updates the display position if required.

        :param str_pos: the plugin display position (input) string.
        :returns: the equivalent numerical position of str_pos and and updated\
            str_pos.
        :rtype: (pos, str_pos)
        """
        pos_list = self.get_split_positions()
        num = re.findall("\d+", str_pos)[0]
        letter = re.findall("[a-z]", str_pos)
        entry = [num, letter[0]] if letter else [num]

        # full value already exists in the list
        if entry in pos_list:
            index = pos_list.index(entry)
            return self.inc_positions(index, pos_list, entry, 1)

        # only the number exists in the list
        num_list = [pos_list[i][0] for i in range(len(pos_list))]
        if entry[0] in num_list:
            start = num_list.index(entry[0])
            if len(entry) is 2:
                if len(pos_list[start]) is 2:
                    idx = int([i for i in range(len(num_list)) if
                               (num_list[i] == entry[0])][-1])+1
                    entry = [entry[0], str(unichr(ord(pos_list[idx-1][1])+1))]
                    return idx, ''.join(entry)
                if entry[1] == 'a':
                    self.plugin_list.plugin_list[start]['pos'] = entry[0] + 'b'
                    return start, ''.join(entry)
                else:
                    self.plugin_list.plugin_list[start]['pos'] = entry[0] + 'a'
                    return start+1, entry[0] + 'b'
            return self.inc_positions(start, pos_list, entry, 1)

        # number not in list
        entry[0] = str(int(num_list[-1])+1 if num_list else 1)
        if len(entry) is 2:
            entry[1] = 'a'
        return len(self.plugin_list.plugin_list), ''.join(entry)

    def increment_positions(self):
        """ Update old process lists that start plugin numbering from 0 to
        start from 1. """
        for plugin in self.plugin_list.plugin_list:
            str_pos = plugin['pos']
            num = str(int(re.findall("\d+", str_pos)[0]) + 1)
            letter = re.findall("[a-z]", str_pos)
            plugin['pos'] = ''.join([num, letter[0]] if letter else [num])

    def get_positions(self):
        """ Get a list of all current plugin entry positions. """
        elems = self.plugin_list.plugin_list
        pos_list = []
        for e in elems:
            pos_list.append(e['pos'])
        return pos_list

    def get_split_positions(self):
        """ Separate numbers and letters in positions. """
        positions = self.get_positions()
        split_pos = []
        for i in range(len(positions)):
            num = re.findall('\d+', positions[i])[0]
            letter = re.findall('[a-z]', positions[i])
            split_pos.append([num, letter[0]] if letter else [num])
        return split_pos

    def find_position(self, pos):
        """ Find the numerical index of a position (a string). """
        pos_list = self.get_positions()
        if not pos_list:
            print('There are no items to access in your list.')
            raise Exception('Please add an item to the process list.')
        else:
            if pos not in pos_list:
                raise Exception("Incorrect plugin position.")
            return pos_list.index(pos)

    def inc_positions(self, start, pos_list, entry, inc):
        if len(entry) is 1:
            self.inc_numbers(start, pos_list, inc)
        else:
            idx = [i for i in range(start, len(pos_list)) if
                   pos_list[i][0] == entry[0]]
            self.inc_letters(idx, pos_list, inc)
        return start, ''.join(entry)

    def inc_numbers(self, start, pos_list, inc):
        for i in range(start, len(pos_list)):
            pos_list[i][0] = str(int(pos_list[i][0])+inc)
            self.plugin_list.plugin_list[i]['pos'] = ''.join(pos_list[i])

    def inc_letters(self, idx, pos_list, inc):
        for i in idx:
            pos_list[i][1] = str(unichr(ord(pos_list[i][1])+inc))
            self.plugin_list.plugin_list[i]['pos'] = ''.join(pos_list[i])

    def insert(self, plugin, pos, str_pos, replace=False):
        plugin_dict = self.create_plugin_dict(plugin)
        plugin_dict['pos'] = str_pos
        if replace:
            self.plugin_list.plugin_list[pos] = plugin_dict
        else:
            self.plugin_list.plugin_list.insert(pos, plugin_dict)

    def create_plugin_dict(self, plugin):
        plugin_dict = {}
        plugin_dict['name'] = plugin.name
        plugin_dict['id'] = plugin.__module__
        plugin_dict['data'] = plugin.parameters
        plugin_dict['active'] = True
        plugin_dict['tools'] = plugin.tools
        plugin_dict['param'] = plugin.p_dict
        plugin_dict['doc'] = plugin.docstring_info
        return plugin_dict

    def get(self, pos):
        return self.plugin_list.plugin_list[pos]

    def cite(self, pos):
        if pos >= self.size:
            raise Exception("Cannot find citations for this plugin %s as it does not exist."
                            % self.plugin_list.plugin_list[pos]['name'])
        p_cite = self.plugin_list.plugin_list[pos]['tools'].get_citations()
        # To Do - Citation storage and display
        for k, v in p_cite.items():
            if v.get('bibtex'):
                print(v['bibtex'])

    def remove(self, pos):
        if pos >= self.size:
            raise Exception("Cannot remove plugin %s as it does not exist."
                            % self.plugin_list.plugin_list[pos]['name'])
        pos_str = self.plugin_list.plugin_list[pos]['pos']
        self.plugin_list.plugin_list.pop(pos)
        pos_list = self.get_split_positions()
        self.inc_positions(pos, pos_list, pos_str, -1)

    def size(self):
        return len(self.plugin_list.plugin_list)
