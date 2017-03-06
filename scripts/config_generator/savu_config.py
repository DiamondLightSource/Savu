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
import atexit
import logging

from content import Content
from completer import Completer
from display_formatter import ListDisplay, DispDisplay
import arg_parsers as parsers
from savu.plugins import utils as pu
import config_utils as utils
from config_utils import parse_args


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


def _help(content, args):
    """ Display the help information"""
    print('%s Savu configurator commands %s\n' % tuple(['*'*25]*2))
    for key in commands.keys():
        doc = commands[key].__doc__
        if doc:
            print("%8s : %s" % (key, commands[key].__doc__))
    print("\n%s\n* For more information about individual commands type "
          "'<command> -h' *\n%s\n" % tuple(['*'*70]*2))
    return content


@parse_args
def _open(content, args):
    """ Open or create a new process list."""
    if os.path.exists(args.file):
        print("Opening file %s" % (args.file))
        content.plugin_list._populate_plugin_list(args.file, activePass=True)
        # Auto refresh plugin list? # update numbering for old plugin_list
        content.update()
        formatter = DispDisplay(content.plugin_list)
        content.display(formatter)
    return content


@parse_args
def _disp(content, args):
    """ Display the plugins in the current list."""
    i, j = args.range if isinstance(args.range, list) else [args.range, -1]
    formatter = DispDisplay(content.plugin_list)
    verbosity = parsers._get_verbosity(args)
    level = 'all' if args.all else 'user'
    content.display(formatter, level=level, verbose=verbosity, start=i, stop=j)
    return content


@parse_args
def _list(content, args):
    """ List the available plugins. """
    list_content = Content()
    utils._populate_plugin_list(list_content, pfilter=args.string)
    if not len(list_content.plugin_list.plugin_list):
        print("No plugins were found containing the string %s" % (args.string))
        return content
    formatter = ListDisplay(list_content.plugin_list)
    verbosity = parsers._get_verbosity(args)
    print("-----------------------------------------")
    list_content.display(formatter, verbose=verbosity)
    print("-----------------------------------------")
    return content


@parse_args
def _save(content, args):
    """ Save the current process list."""
    content.save(args.file)
    return content


@parse_args
def _mod(content, args):
    """ Modify plugin parameters. """
    if args.param.split('.'):
        element, subelement = args.param.split('.')
        value = content.value(args.value)
        content.modify(element+1, subelement, value)
        content.display(start=element, stop=element+1)
    else:
        print("The parameter %s was not recognised." % args.param)
    return content


@parse_args
def _set(content, arg):
    """ Set the status of the plugin to be on or off. """
    args = parsers._set_arg_parser(arg.split(), _list.__doc__)
    if not args:
        return content
    content.on_and_off(args.plugin_no, args.status.upper())
    content.display(start=args.plugin_no, stop=args.plugin+1)
    return content


@parse_args
def _add(content, args):
    """ Add a plugin to the list. """
    formatter = DispDisplay(content.plugin_list)
    elems = content.get_positions()
    final = int(list(elems[-1])[0])+1 if elems else 1
    if args.name in pu.plugins.keys():
        print("Adding the plugin %s to the list" % args.name)
        content.add(args.name, args.pos if args.pos else str(final))
        print("plugin should have been added")
        content.display(formatter)
    else:
        print("Sorry the plugin %s is not in my list." % (args.name))
    return content


@parse_args
def _ref(content, args):
    """ Refresh a plugin (update it). """
    formatter = DispDisplay(content.plugin_list)
    positions = content.get_positions() if args.pos is ['*'] else args.pos
    for pos_str in positions:
        pos = content.find_position(pos_str)
        if pos < 0 or pos >= len(content.plugin_list.plugin_list):
            print("Sorry %s is out of range" % (args))
            return content
        content.refresh(pos)
        name = content.plugin_list.plugin_list[pos]['name']
        default_vals = content.get(pos)['data'] if args.defaults else None
        content.replace(name, pos_str, default_vals)
        content.display(formatter, start=pos, stop=pos+1)
    return content


@parse_args
def _rem(content, args):
    """ Remove plugin(s) from the list. """
    for pos_str in args.pos:
        pos = content.find_position(pos_str)
        if pos < 0 or pos >= len(content.plugin_list.plugin_list):
            print("Sorry %s is out of range" % (pos))
            return content
            content.remove(pos)
    formatter = DispDisplay(content.plugin_list)
    content.display(formatter)
    return content


@parse_args
def _move(content, args):
    """ Move a plugin to a different position in the list."""
    try:
        content.move(args.orig_pos, args.new_pos)
    except:
        print ("Sorry, the information you have given is incorrect")
    return content


@parse_args
def _coll(content, arg):
    """ List all plugin collections. To list all plugins in a collection type
    'list <collection_name>"""
    colls = Completer([])._get_list_commands()
    print("-----------------------------------------")
    for c in colls:
        print(c)
    print("-----------------------------------------")
    return content


def _exit(content, arg):
    """ Close the program."""
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
            'set': _set,
            'add': _add,
            'rem': _rem,
            'move': _move,
            'ref': _ref,
            'coll': _coll,
            'exit': _exit,
            'history': _history}


def main():

    args = parsers._config_arg_parser()
    if not args:
        return

    print("Starting Savu Config tool (please wait for prompt)")

    comp = Completer(commands)
    # we want to treat '/' as part of a word, so override the delimiters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(comp.complete)

    logging.basicConfig(level='CRITICAL')
    pu.populate_plugins()

    content = Content(level="all" if args.disp_all else None)

    while True:
        in_list = raw_input(">>> ").strip().split(' ', 1)
        command, arg = in_list if len(in_list) is 2 else in_list+['']
        command = command if command else 'help'
        if command not in commands:
            print("I'm sorry, that's not a command I recognise. Type 'help' "
                  "for a list of available Savu commands.")
        else:
            content = commands[command](content, arg)

        if content.is_finished():
            break

        # write the history to the history file
        readline.write_history_file(histfile)

    print("Thanks for using the application")

if __name__ == '__main__':
    main()
