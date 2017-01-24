# Copyright 2015 Diamond Light Source Ltd.
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

'''
Created on 21 May 2015

@author: ssg37927
'''

from __future__ import print_function

import os
from savu.data.plugin_list import PluginList
from savu.plugins import utils as pu
import re

if os.name == 'nt':
    import win_readline as readline
else:
    import readline

from colorama import Fore, Back, init
#Need to call init method for colorama to work in windows
init()

RE_SPACE = re.compile('.*\s+$', re.M)
histfile = os.path.join(os.path.expanduser("~"), ".savuhist")
try:
    readline.read_history_file(histfile)
    readline.set_history_length(1000)
except IOError:
    pass
import atexit
atexit.register(readline.write_history_file, histfile)


class Content(object):

    def __init__(self, filename):
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
            print("switching plugin", element, "ON")
            self.plugin_list.plugin_list[element]['active'] = True
        else:
            print("switching plugin", element, "OFF")
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
        process = {}
        process['name'] = plugin.name
        process['id'] = plugin.__module__
        process['pos'] = str_pos
        process['data'] = plugin.parameters
        process['active'] = True
        process['desc'] = plugin.parameters_desc
        if replace:
            self.plugin_list.plugin_list[pos] = process
        else:
            self.plugin_list.plugin_list.insert(pos, process)

    def get(self, pos):
        return self.plugin_list.plugin_list[pos]

    def remove(self, pos):
        entry = self.plugin_list.plugin_list[pos]['pos']
        self.plugin_list.plugin_list.pop(pos)
        pos_list = self.get_split_positions()
        self.inc_positions(pos, pos_list, entry, -1)

    def size(self):
        return len(self.plugin_list.plugin_list)


def _help(content, arg):
    """Display the help information"""
    for key in commands.keys():
        print("%4s : %s" % (key, commands[key].__doc__))
    return content


def _open(content, arg):
    """Opens or creates a new configuration file with the given filename"""
    ct = Content(arg)
    ct.display()
    return ct


def _disp(content, arg):
    """Displays the process in the current list.
       Optional arguments:
            i(int): Display the ith item in the list.
            i(int) j(int): Display list items i to j.
            -q: Quiet mode. Only process names are listed.
            -v: Verbose mode. Displays parameter details.
            -vv: Extra verbose. Displays additional information and warnings.
            """
    verbosity = ['-vv', '-v', '-q']
    idx = {'start': 0, 'stop': -1}
    if arg:
        split_arg = arg.split(' ')
        for v in verbosity:
            if v in split_arg:
                idx['verbose'] = v
                split_arg.remove(v)
        len_args = len(split_arg)
        if len_args > 0:
            try:
                idx['start'] = content.find_position(split_arg[0])
                idx['stop'] = idx['start']+1 if len_args == 1 else\
                    content.find_position(split_arg[1])+1
            except ValueError:
                print("The arguments %s are unknown", arg)
    content.display(**idx)
    return content


def _list(content, arg):
    """List the plugins which have been registered for use.
       Optional arguments:
            type(str): Display 'type' plugins. Where type can be 'loaders',
            'corrections', 'filters', 'reconstructions', 'savers' or the start\
            of a plugin name followed by an asterisk, e.g. a*.
            -q: Quiet mode. Only process names are listed.
            -v: Verbose mode. Process names, synopsis and parameters.
    """

    verbosity = ['-q', '-v', '-vv']
    if arg:
        arg = arg.split(' ')

    if len(arg) is 2:
        plugins = _order_plugins(pfilter=arg[0])
        arg = [arg[1]]
    elif len(arg) is 1 and arg[0] not in verbosity:
        plugins = _order_plugins(pfilter=arg[0])
        arg = None
    else:
        plugins = _order_plugins()

    print("-----------------------------------------")
    for key, value in plugins:
        if not arg:
            print(key, content.plugin_list._get_synopsis(
                key, 60, Fore.CYAN, Fore.RESET))
        elif arg[0] == '-q':
            print(key)
        elif arg[0] == '-v':
            plugin = pu.plugins[key]()
            plugin._populate_default_parameters()
            print(key, content.plugin_list._get_synopsis(
                key, 60, Fore.CYAN, Fore.RESET),
                content.plugin_list._get_param_details(plugin.parameters, 100))
        else:
            print("The arguments %s are unknown", arg)
    print("-----------------------------------------")
    return content


def _order_plugins(pfilter=""):
    key_list = []
    value_list = []
    star_search = \
        pfilter.split('*')[0] if pfilter and '*' in pfilter else False

    for key, value in pu.plugins.iteritems():
        if star_search:
            search = '(?i)^' + star_search
            if re.match(search, value.__name__) or \
                    re.match(search, value.__module__):
                key_list.append(key)
                value_list.append(value)
        elif pfilter in value.__module__ or pfilter in value.__name__:
            key_list.append(key)
            value_list.append(value)

    sort_idx = sorted(range(len(key_list)), key=lambda k: key_list[k])
    key_list.sort()
    value_list = [value_list[i] for i in sort_idx]
    return zip(key_list, value_list)


def _params(content, arg):
    """Displays the parameters of the specified plugin.
    """
    try:
        plugin = pu.plugins[arg]()
        plugin._populate_default_parameters()
        print("-----------------------------------------")
        print(arg)
        for p_key in plugin.parameters.keys():
            print("    %20s : %s" % (p_key, plugin.parameters[p_key]))
        print("-----------------------------------------")
        return content
    except:
        print("Sorry I can't process the argument '%s'" % (arg))
    return content


def _save(content, arg):
    """Save the current list to disk with the filename given"""
    content.save(arg)
    return content


def _mod(content, arg):
    """Modifies the target value e.g. 'mod 1.value 27' and turns the plugins on
    and off e.g 'mod 1.on' or 'mod 1.off'
    """
    on_off_list = ['ON', 'on', 'OFF', 'off']
    try:
        element,  subelement = arg.split()[0].split('.')
        element = content.find_position(element)
        if subelement in on_off_list:
            content.on_and_off(element, on_off_list.index(subelement))
        else:
            value = content.value(arg)
            # change element here
            content.modify(element+1, subelement, value)
        # display only the changed element
        content.display(start=element, stop=element+1)
    except:
        print("Sorry I can't process the argument '%s'" % (arg))
    return content


def _add(content, arg):
    """Adds the named plugin before the specified location 'MedianFilter 2'"""
    try:
        args = arg.split()
        name = args[0]
        elems = content.get_positions()
        final = int(list(elems[-1])[0])+1 if elems else 1
        pos = args[1] if len(args) == 2 else str(final)
        if name in pu.plugins.keys():
            content.add(name, pos)
        else:
            print("Sorry the plugin %s is not in my list, pick one from list" %
                  (name))
    except Exception as e:
        print("Sorry I can't process the argument '%s'" % (arg))
        print(e)
    return content


def _ref(content, arg):
    """Refreshes the plugin, replacing it with itself (updating any changes).
       Optional arguments:
            -r: Keep parameter values (if the parameter still exists).
                Without this flag the parameters revert to default values.
    """

    if not arg:
        print("ref requires the process number or * as argument")
        print("e.g. 'ref 1' refreshes process 1")
        print("e.g. 'ref *' refreshes ALL processes")
        return content

    kwarg = None
    if len(arg.split()) > 1:
        arg, kwarg = arg.split()

    positions = content.get_positions() if arg is '*' else [arg]
    for pos_str in positions:
        pos = content.find_position(pos_str)
        if pos < 0 or pos >= len(content.plugin_list.plugin_list):
            print("Sorry %s is out of range" % (arg))
            return content
        name = content.plugin_list.plugin_list[pos]['name']
        keep = content.get(pos)['data'] if kwarg else None
        content.replace(name, pos_str, keep)
        content.display(start=pos, stop=pos+1)

    return content


def _rem(content, arg):
    """Remove the numbered item from the list"""
    pos = content.find_position(arg)
    if pos < 0 or pos >= len(content.plugin_list.plugin_list):
            print("Sorry %s is out of range" % (arg))
            return content
    content.remove(pos)
    content.display()
    return content


def _move(content, arg):
    """ Moves the plugin from position a to b: 'move a b'. e.g 'move 1 2'."""
    if len(arg.split()) is not 2:
        print ("The move command takes two arguments: e.g 'move 1 2' moves "
               "from position 1 to position 2")
        return content
    try:
        old_pos_str, new_pos_str = arg.split()
        content.move(old_pos_str, new_pos_str)
    except:
        print ("Sorry, the information you have given is incorrect")
        return content
    return content


def _exit(content, arg):
    """Close the program"""
    content.set_finished(content.save("exit"))
    return content


def _history(content, arg):
    hlen = readline.get_current_history_length()
    for i in range(hlen):
        print("%5i : %s" % (i, readline.get_history_item(i)))
    return content


commands = {'open': _open,
            'help': _help,
            'disp': _disp,
            'list': _list,
            'save': _save,
            'mod': _mod,
            'add': _add,
            'rem': _rem,
            'move': _move,
            'ref': _ref,
            'params': _params,
            'exit': _exit,
            'history': _history}

list_commands = ['loaders',
                 'corrections',
                 'filters',
                 'reconstructions',
                 'savers']


class Completer(object):

    def _listdir(self, root):
        "List directory 'root' appending the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
               for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def path_complete(self, args):
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])

    def complete_open(self, args):
        "Completions for the open commands."
        return self.path_complete(args)

    def complete_save(self, args):
        "Completions for the save commands."
        return self.path_complete(args)

    def complete_list(self, args):
        if not args[0]:
            return list_commands
        return [x for x in list_commands if x.startswith(args[0])]

    def complete_params(self, args):
        if not args[0]:
            return pu.plugins.keys()
        return [x for x in pu.plugins.keys() if x.startswith(args[0])]

    def complete(self, text, state):
        "Generic readline completion entry point."
        read_buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all commands
        if not line:
            return [c + ' ' for c in commands.keys()][state]
        # account for last argument ending in a space
        if RE_SPACE.match(read_buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in commands.keys():
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]
        results = \
            [c + ' ' for c in commands.keys() if c.startswith(cmd)] + [None]
        return results[state]


def main():
    print("Starting Savu Config tool (please wait for prompt)")

    comp = Completer()
    # we want to treat '/' as part of a word, so override the delimiters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(comp.complete)


    # load all the packages in the plugins directory to register classes
    # I've changed this to be in plugin utils package since this is now also called from dawn when 
    #it populates savu plugins. adp 14/12/16
    pu.populate_plugins()


    # set up things
    input_string = "startup"
    content = Content("")

    while True:
        input_string = raw_input(">>> ").strip()

        if len(input_string) == 0:
            command = 'help'
            arg = ""
        else:
            command = input_string.split()[0]
            arg = ' '.join(input_string.split()[1:])

        # try to run the command
        if command in commands.keys():
            content = commands[command](content, arg)
        else:
            print("I'm sorry, thats not a command I recognise, try help")

        if content.is_finished():
            break

        # write the history to the history file
        readline.write_history_file(histfile)

    print("Thanks for using the application")


if __name__ == '__main__':
    main()
