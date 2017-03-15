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

from content import Content
from completer import Completer
from display_formatter import ListDisplay, DispDisplay
import arg_parsers as parsers
from savu.plugins import utils as pu
import config_utils as utils
from config_utils import parse_args
from config_utils import error_catcher


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
@error_catcher
def _open(content, args):
    """ Open or create a new process list."""
    content.fopen(args.file, update=True, skip=args.skip)
    _ref(content, '* -n')
    _disp(content, '-q')
    return content


@parse_args
@error_catcher
def _disp(content, args):
    """ Display the plugins in the current list."""
    range_dict = utils.__get_start_stop(content, args.start, args.stop)
    formatter = DispDisplay(content.plugin_list)
    verbosity = parsers._get_verbosity(args)
    level = 'all' if args.all else content.disp_level
    content.display(formatter, level=level, verbose=verbosity, **range_dict)
    return content


@parse_args
@error_catcher
def _list(content, args):
    """ List the available plugins. """
    list_content = Content()
    utils._populate_plugin_list(list_content, pfilter=args.string)

    # ******* move this to content class as exception
    if not len(list_content.plugin_list.plugin_list):
        print("No result found.")
        return content
    formatter = ListDisplay(list_content.plugin_list)
    verbosity = parsers._get_verbosity(args)
    list_content.display(formatter, verbose=verbosity)
    return content


@parse_args
@error_catcher
def _save(content, args):
    """ Save the current process list to file."""
    out_file = content.filename if args.input else args.filepath
    DispDisplay(content.plugin_list)._notices()
    content.save(out_file)
    return content


@parse_args
@error_catcher
def _mod(content, args):
    """ Modify plugin parameters. """
    pos_str, subelem = args.param.split('.')
    pos = content.modify(pos_str, subelem, args.value)
    formatter = DispDisplay(content.plugin_list)
    content.display(formatter, start=pos, stop=pos+1)
    return content


@parse_args
@error_catcher
def _set(content, arg):
    """ Set the status of the plugin to be on or off. """
    args = parsers._set_arg_parser(arg.split(), _list.__doc__)
    if not args:
        return content
    content.on_and_off(args.plugin_no, args.status.upper())
    content.display(start=args.plugin_no, stop=args.plugin+1)
    return content


@parse_args
@error_catcher
def _add(content, args):
    """ Add a plugin to the list. """
    formatter = DispDisplay(content.plugin_list)
    elems = content.get_positions()
    final = str(int(list(elems[-1])[0])+1) if elems else 1
    if args.name in pu.plugins.keys():
        content.add(args.name, args.pos if args.pos else str(final))
        content.display(formatter)
    else:
        print("Sorry the plugin %s does not exist." % (args.name))
    return content


@parse_args
@error_catcher
def _ref(content, args):
    """ Refresh a plugin (update it). """
    formatter = DispDisplay(content.plugin_list)
    positions = content.get_positions() if args.pos == ['*'] else args.pos
    for pos_str in positions:
        pos = content.find_position(pos_str)
        content.refresh(pos_str, defaults=args.defaults)
        if not args.nodisp:
            content.display(formatter, start=pos, stop=pos+1)
    return content


@parse_args
@error_catcher
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
@error_catcher
def _move(content, args):
    """ Move a plugin to a different position in the list."""
    try:
        content.move(args.orig_pos, args.new_pos)
    except:
        print ("ERROR: Please type 'move -h' for help.")
    return content


@parse_args
@error_catcher
def _coll(content, arg):
    """ List all plugin collections. """
    colls = Completer([])._get_collections()
    print("-----------------------------------------")
    for c in colls:
        print(c)
    print("-----------------------------------------")
    return content


def _exit(content, arg):
    """ Close the program."""
    content.set_finished()
    return content


def _history(content, arg):
    hlen = utils.readline.get_current_history_length()
    for i in range(hlen):
        print("%5i : %s" % (i, utils.readline.get_history_item(i)))
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
    if args.error:
        utils.error_level = 1

    print("Starting Savu Config tool (please wait for prompt)")

    pu.populate_plugins()
    comp = Completer(commands=commands, plugin_list=pu.plugins)
    utils._set_readline(comp.complete)

    content = Content(level="all" if args.disp_all else None)

    # if file flag is passed then open it here
    if args.file:
        commands['open'](content, args.file)

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
        utils.readline.write_history_file(utils.histfile)

    print("Thanks for using the application")

if __name__ == '__main__':
    main()
