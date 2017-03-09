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

import re
import os

from savu.plugins import utils as pu
from savu.data.plugin_list import PluginList
from colorama import Fore, Back, init
import deprecated_dict
#  Need to call init method for colorama to work in windows
init()


class Content(object):

    def __init__(self, filename=None, level='user'):
        self.disp_level = level
        self.plugin_list = PluginList()
        self.filename = filename
        self._finished = False

    def set_finished(self):
        i = raw_input("Are you sure? [y/N]")
        self._finished = True if i.lower() == 'y' else False

    def is_finished(self):
        return self._finished

    def fopen(self, infile):
        if os.path.exists(infile):
            self.plugin_list._populate_plugin_list(infile, activePass=True)
        else:
            raise Exception('INPUT ERROR: The file does not exist.')
        self.filename = infile
        # updating old process lists
        the_list = self.plugin_list.plugin_list
        if 'pos' in the_list[0].keys() and the_list[0]['pos'] == '0':
            self.increment_positions()
        # replace deprecated plugins
        self._apply_plugin_updates()
            

        # ensure 'active' is now in list and remove this condition in pluginlist.
        # ensure all numbers start from 1 and remove this condition in pluginlist        

#        print("Sorry, this process list is incompatible with this version of "
#              "Savu and cannot be auto-updated.  Please re-create the list.")


    def display(self, formatter, **kwargs):
        print '\n' + formatter._get_string(**kwargs), '\n'

    def save(self, filename):
        i = raw_input("Are you sure you want to save the current data to "
                      "'%s' [y/N]" % (filename))
        if i.lower() == 'y':
            if not os.path.exists(os.path.dirname(filename)):
                file_error = "INPUT_ERROR: There is an error in the filepath."
                raise Exception(file_error)
            print("Saving file %s" % (filename))
            self.plugin_list._save_plugin_list(filename)
        else:
            print("The process list has NOT been saved.")

    def add(self, name, str_pos):
        plugin = pu.plugins[name]()
        plugin._populate_default_parameters()
        pos, str_pos = self.convert_pos(str_pos)
        self.insert(plugin, pos, str_pos)

    def refresh(self, str_pos, defaults=False):
        pos = self.find_position(str_pos)
        name = self.plugin_list.plugin_list[pos]['name']
        plugin = pu.plugins[name]()
        plugin._populate_default_parameters()

        keep = self.get(pos)['data'] if not defaults else None
        self.insert(plugin, pos, str_pos, replace=True)
        if keep:
            union_params = set(keep).intersection(set(plugin.parameters))
            for param in union_params:
                self.modify(str_pos, param, keep[param], ref=True)

    def _apply_plugin_updates(self):
        missing = False
        for plugin in self.plugin_list.plugin_list:
            if 'active' not in plugin.keys():
                plugin['active'] = True
            if plugin['name'] not in pu.plugins.keys():
                if not self._investigate_plugins(plugin['name']):
                    missing = True
        if missing:
            raise Exception('PLUGIN ERROR: To skip missing plugins type '
                            '"open <process_list> -r."')

    def _investigate_plugins(self, name):
        """ Renames a plugin that has been replaced or had a name change. """
        for key in pu.plugins.keys():
            if name.lower() == key.lower():
                return key

        if name in deprecated_dict.entries.keys():
            new_name = deprecated_dict.entries[name]
            print new_name
            if new_name in pu.plugins.keys():
                print ("new name has been found")
                print('AUTO-REPLACEMENT: The plugin %s is no longer available '
                      'and has been replaced by %s.  Please check the '
                      'parameters' % (name, new_name))
                return new_name
        print('The plugin %s is no longer available.' % name)
        return None

    def move(self, old, new):
        old_pos = self.find_position(old)
        entry = self.plugin_list.plugin_list[old_pos]
        self.remove(old_pos)
        new_pos, new = self.convert_pos(new)
        name = entry['name']
        if name in pu.plugins.keys():
            self.insert(pu.plugins[name](), new_pos, new)
        else:
            print("Sorry the plugin %s is not in my list, pick one from list" %
                  (name))
            return
        self.plugin_list.plugin_list[new_pos] = entry
        self.plugin_list.plugin_list[new_pos]['pos'] = new
        self.display()

    def modify(self, pos_str, subelem, value, ref=False):
        if not ref:
            value = self.value(value)
        pos = self.find_position(pos_str)
        data_elements = self.plugin_list.plugin_list[pos]['data']
        if subelem.isdigit():
            data_elements[data_elements.keys()[int(subelem)-1]] = value
        else:
            data_elements[subelem] = value
        return pos

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

    def on_and_off(self, element, index):
        print("switching plugin %d %s" % element+1, index)
        status = True if index == 'ON' else False
        self.plugin_list.plugin_list[element]['active'] = status

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
        if pos not in pos_list:
            raise Exception("INPUT ERROR: Incorrect plugin position.")
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
        plugin_dict['desc'] = plugin.parameters_desc
        plugin_dict['hide'] = plugin.parameters_hide
        plugin_dict['user'] = plugin.parameters_user
        return plugin_dict

    def get(self, pos):
        return self.plugin_list.plugin_list[pos]

    def remove(self, pos):
        entry = self.plugin_list.plugin_list[pos]['pos']
        self.plugin_list.plugin_list.pop(pos)
        pos_list = self.get_split_positions()
        self.inc_positions(pos, pos_list, entry, -1)

    def size(self):
        return len(self.plugin_list.plugin_list)
