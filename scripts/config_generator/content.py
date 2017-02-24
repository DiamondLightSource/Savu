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

import os
import re

from savu.plugins import utils as pu
from savu.data.plugin_list import PluginList
from colorama import Fore, Back, init
#  Need to call init method for colorama to work in windows
init()


class Content(object):

    def __init__(self, filename, options):
        self.disp_level = 'all' if options.disp_all else 'user'
        filename = options.input_file if options.input_file else filename
        self.plugin_list = PluginList()
        self.filename = filename
        self._finished = False
        if os.path.exists(filename):
            print("Opening file %s" % (filename))
            self.plugin_list._populate_plugin_list(filename, activePass=True)

    def set_finished(self, value):
        self._finished = value

    def is_finished(self):
        return self._finished

    def display(self, **kwargs):
        if 'level' not in kwargs.keys():
            kwargs['level'] = self.disp_level
        print ('\n' + self.plugin_list._get_string(**kwargs), '\n')

    def save(self, filename):
        if filename is not "" and filename is not "exit":
            self.filename = filename

        if filename == "exit":
            i = raw_input("Are you sure? [y/N]")
            return True if i.lower() == 'y' else False

        width = 86
        warnings = self.get_warnings(width)
        if warnings:
            notice = Back.RED + Fore.WHITE + "IMPORTANT PLUGIN NOTICES" +\
                Back.RESET + Fore.RESET + "\n"
            border = "*"*width + '\n'
            print (border + notice + warnings + '\n'+border)
        i = raw_input("Are you sure you want to save the current data to "
                      "'%s' [y/N]" % (self.filename))
        if i.lower() == 'y':
            print("Saving file %s" % (self.filename))
            self.plugin_list._save_plugin_list(self.filename)
        else:
            print("The process list has NOT been saved.")

    def get_warnings(self, width):
        colour = Back.RESET + Fore.RESET
        warnings = []
        for plugin in self.plugin_list.plugin_list:
            warn = self.plugin_list._get_docstring_info(plugin['name'])['warn']
            if warn:
                for w in warn.split('\n'):
                    string = plugin['name'] + ": " + w
                    warnings.append(self.plugin_list._get_equal_lines(
                        string, width-1, colour, colour, " "*2))
        return "\n".join(
            ["*" + "\n ".join(w.split('\n')) for w in warnings if w])

    def value(self, arg):
        value = ([''.join(arg.split()[1:])][0]).split()[0]
        tuning = True if value.count(';') else False
        if not tuning:
            try:
                exec("value = " + value)
            except (NameError, SyntaxError):
                exec("value = " + "'" + value + "'")
        return value

    def add(self, name, str_pos):
        plugin = pu.plugins[name]()
        plugin._populate_default_parameters()
        pos, str_pos = self.convert_pos(str_pos)
        self.insert(plugin, pos, str_pos)
        self.display()

    def replace(self, name, str_pos, keep):
        plugin = pu.plugins[name]()
        plugin._populate_default_parameters()
        pos = self.find_position(str_pos)
        self.insert(plugin, pos, str_pos, replace=True)
        if keep:
            union_params = set(keep).intersection(set(plugin.parameters))
            for param in union_params:
                self.modify(pos+1, param, keep[param])

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

    def modify(self, element, subelement, value):
        data_elements = self.plugin_list.plugin_list[element-1]['data']
        try:
            position = int(subelement) - 1
            data_elements[data_elements.keys()[position]] = value
        except:
            if subelement in data_elements.keys():
                data_elements[subelement] = value
            else:
                print("Sorry, element %i does not have a %s parameter" %
                      (element, subelement))

    def convert_to_ascii(self, value):
        ascii_list = []
        for v in value:
            ascii_list.append(v.encode('ascii', 'ignore'))
        return ascii_list

    def on_and_off(self, element, index):
        if index < 2:
            print("switching plugin", element+1, "ON")
            self.plugin_list.plugin_list[element]['active'] = True
        else:
            print("switching plugin", element+1, "OFF")
            self.plugin_list.plugin_list[element]['active'] = False

    def convert_pos(self, str_pos):
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

    def get_positions(self):
        elems = self.plugin_list.plugin_list
        pos_list = []
        for e in elems:
            pos_list.append(e['pos'])
        return pos_list

    def get_split_positions(self):
        positions = self.get_positions()
        split_pos = []
        for i in range(len(positions)):
            num = re.findall('\d+', positions[i])[0]
            letter = re.findall('[a-z]', positions[i])
            split_pos.append([num, letter[0]] if letter else [num])
        return split_pos

    def find_position(self, pos):
        pos_list = self.get_positions()
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
