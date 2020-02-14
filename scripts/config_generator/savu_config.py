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
.. module:: savu_config.py
   :platform: Unix
   :synopsis: A command line tool for creating Savu plugin lists

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from __future__ import print_function

import re
import sys

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
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
    print('%s Savu (local) configurator commands %s\n' % tuple(['*'*21]*2))
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
    """ Open an existing process list."""
    content.fopen(args.file, update=True, skip=args.skip)
    _ref(content, '* -n')
    _disp(content, '-q')
    return content


@parse_args
@error_catcher
def _disp(content, args):
    """ Display the plugins in the current list."""
    try:
        range_dict = utils.__get_start_stop(content, args.start, args.stop)
        formatter = DispDisplay(content.plugin_list)
        verbosity = parsers._get_verbosity(args)
        level = 'all' if args.all else content.disp_level
        content.display(formatter, level=level, verbose=verbosity, **range_dict)
        return content
    except:
        raise

@parse_args
@error_catcher
def _list(content, args):
    """ List the available plugins. """
    list_content = Content()
    utils._populate_plugin_list(list_content, pfilter=args.string)
    if not len(list_content.plugin_list.plugin_list):
        print("No result found.")
        return content

    # Sort the list of dictionaries. Sort by the name of the plugin within each dictionary
    list_content.plugin_list.plugin_list = sorted(list_content.plugin_list.plugin_list, key=lambda i: i['name'])

    formatter = ListDisplay(list_content.plugin_list)
    verbosity = parsers._get_verbosity(args)
    list_content.display(formatter, verbose=verbosity)
    return content

@parse_args
@error_catcher
def _save(content, args):
    """ Save the current process list to file."""

    # Check if the plug in list has been populated.
    if len(content.plugin_list.plugin_list):
        # Check if a loader and saver are present.
        content.plugin_list._check_loaders_and_savers()
        out_file = content.filename if args.input else args.filepath
        content.check_file(out_file)
        DispDisplay(content.plugin_list)._notices()
        content.save(out_file, check=raw_input("Are you sure you want to save the "
                     "current data to %s' [y/N]" % (out_file)),
                     template=args.template)

    raise Exception("No items were found in your process list. Type 'add' to add a plugin to the list.")
    return content


@parse_args
@error_catcher
def _mod(content, args):
    """ Modify plugin parameters. """
    try:
        pos_str, subelem = args.param.split('.')
        try:
            content.modify(pos_str, subelem, ' '.join(args.value))
        except Exception as e:
            print('Error modifying the parameter.')
            print(e)
            raise
        # If modified then display, and show recommendations
        _disp(content, str(args.param) + ' -vv')
    except ValueError:
        print('Incorrect parameter number: Please enter the parameter number to'
              ' select the parameter you want to modify. Use a decimal format.')
        # Otherwise message is - ValueError: need more than 1 value to unpack
    return content


@parse_args
@error_catcher
def _set(content, args):
    """ Set the status of the plugin to be on or off. """
    for pos in args.plugin_pos:
        content.on_and_off(pos, args.status.upper())
    _disp(content, '-q')
    return content


@parse_args
@error_catcher
def _add(content, args):
    """ Add a plugin to the list. """
    elems = content.get_positions()
    final = str(int(re.findall(r'\d+', elems[-1])[0])+1) if elems else 1
    content.add(args.name, args.pos if args.pos else str(final))
    _disp(content, '-q')
    return content


@parse_args
@error_catcher
def _ref(content, args):
    """ Refresh a plugin (update it). """
    positions = content.get_positions() if args.pos == ['*'] else args.pos
    for pos_str in positions:
        content.refresh(pos_str, defaults=args.defaults)
        if not args.nodisp:
            _disp(content, pos_str)
    return content


@parse_args
@error_catcher
def _rem(content, args):
    """ Remove plugin(s) from the list. """
    content.remove(content.find_position(args.pos))
    _disp(content, '-q')
    return content


@parse_args
@error_catcher
def _move(content, args):
    """ Move a plugin to a different position in the list."""
    content.move(args.orig_pos, args.new_pos)
    _disp(content, '-q')
    return content


@parse_args
@error_catcher
def _coll(content, arg):
    """ List all plugin collections. """
    colls = Completer([])._get_collections()
    print('\n')
    for c in colls:
        print('%s\n %s' % ('-'*40, c))
    print('-'*40, '\n')
    return content


def _clear(content, arg):
    """ Clear the current plugin list."""
    content.clear(check=raw_input("Are you sure you want to clear the current "
                  "plugin list? [y/N]"))
    return content


def _exit(content, arg):
    """ Close the program."""
    content.set_finished(check=raw_input("Are you sure? [y/N]"))
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
            'clear': _clear,
            'exit': _exit,
            'history': _history}


def main():

    print("Running the configurator")
    # required for travis tests
    if len(sys.argv) > 2 and sys.argv[-2] == 'scripts/configurator_tests/':
        sys.argv = [sys.argv[:-2]]

    args = parsers._config_arg_parser()
    if args.error:
        utils.error_level = 1

    print("Starting Savu Config tool (please wait for prompt)")

    _reduce_logging_level()

    content = Content(level="all" if args.disp_all else 'user')

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        content.failed = utils.populate_plugins(error_mode=args.error)

    comp = Completer(commands=commands, plugin_list=pu.plugins)
    utils._set_readline(comp.complete)


    # if file flag is passed then open it here
    if args.file:
        commands['open'](content, args.file)

    print("\n*** Press Enter for a list of available commands. ***\n")

    while True:
        try:
            in_list = raw_input(">>> ").strip().split(' ', 1)
        except KeyboardInterrupt:
            print()
            continue

        command, arg = in_list if len(in_list) is 2 else in_list+['']
        command = command if command else 'help'
        if command not in commands:
            print("I'm sorry, that's not a command I recognise. Press Enter "
                  "for a list of available commands.")
        else:
            content = commands[command](content, arg)

        if content.is_finished():
            break

        # write the history to the history file
        utils.readline.write_history_file(utils.histfile)

    print("Thanks for using the application")

def _reduce_logging_level():
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)

if __name__ == '__main__':
    main()
