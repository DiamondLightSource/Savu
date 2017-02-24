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
import re
import atexit
from content import Content
from completer import Completer
from savu.plugins import utils as pu
from colorama import Fore, init
#  Need to call init method for colorama to work in windows
init()

if os.name == 'nt':
    import win_readline as readline
else:
    import readline

histfile = os.path.join(os.path.expanduser("~"), ".savuhist")
try:
    readline.read_history_file(histfile)
    readline.set_history_length(1000)
except IOError:
    pass
atexit.register(readline.write_history_file, histfile)


def _help(content, arg):
    """Display the help information"""
    for key in commands.keys():
        print("%4s : %s" % (key, commands[key].__doc__))
    return content


def _open(content, arg):
    """Opens or creates a new configuration file with the given filename"""
    ct = Content(arg, __option_parser())
    ct.display()
    return ct


def _disp(content, arg):
    """Displays the process in the current list.
       Optional arguments:
            i(int): Display the ith item in the list.
            i(int) j(int): Display list items i to j.
            -a: Display ALL parameters (user parameters only by default).
            -q: Quiet mode. Only process names are listed.
            -v: Verbose mode. Displays parameter details.
            -vv: Extra verbose. Displays additional information and warnings.
            """

    verbosity = ['-vv', '-v', '-q']
    level = content.disp_level
    idx = {'start': 0, 'stop': -1}
    if arg:
        split_arg = arg.split(' ')
        if '-a' in split_arg:
            level = 'all'
            del_idx = split_arg.index('-a')
            del split_arg[del_idx]
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
    content.display(level=level, **idx)
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
            synopsis = content.plugin_list._get_synopsis(
                       key, 60, Fore.CYAN, Fore.RESET)
            params = content.plugin_list._get_param_details(
                     'all', content.create_plugin_dict(plugin), 100)
            print(key, synopsis, params)
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
        content.refresh(pos)
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


def main():
    print("Starting Savu Config tool (please wait for prompt)")

    comp = Completer(commands)
    # we want to treat '/' as part of a word, so override the delimiters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(comp.complete)

    # load all the packages in the plugins directory to register classes
    # I've changed this to be in plugin utils package since this is now also
    # called from dawn when it populates savu plugins. adp 14/12/16
    pu.populate_plugins()

    # set up things
    input_string = "startup"

    content = Content('', __option_parser())

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


def __option_parser():
    """ Option parser for command line arguments.
    """
    import optparse
    desc = "Create process lists of plugins for Savu."
    parser = optparse.OptionParser(description=desc)
    disp_str = "Set the display level to show ALL parameters by default."
    parser.add_option("-a", "--all", action="store_true", dest="disp_all",
                      help=disp_str, default=False)
    input_str = "Open a Savu process list."
    parser.add_option("-i", "--input", dest="input_file", help=input_str)
    (options, args) = parser.parse_args()
    return options

    parser.add_option("-d", "--tmp", dest="temp_dir",
                      help="Store intermediate files in a temp directory.")

if __name__ == '__main__':
    main()
