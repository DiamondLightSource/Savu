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
.. module:: savu_config
   :platform: Unix
   :synopsis: A command line tool for creating Savu plugin lists

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import re
import sys
import logging

logger = logging.getLogger('documentationLog')
logger_rst = logging.getLogger('documentationRst')

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from .content import Content
    from .completer import Completer
    from .display_formatter import ListDisplay, DispDisplay, CiteDisplay
    from . import arg_parsers as parsers
    from savu.plugins import utils as pu
    from . import config_utils as utils
    from .config_utils import parse_args
    from .config_utils import error_catcher


def _help(content, args):
    """ Display the help information"""
    print('%s Savu configurator commands %s\n' % tuple(['*'*21]*2))
    for key in list(commands.keys()):
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
        range_dict = content.get_start_stop(content, args.start, args.stop)
        formatter = DispDisplay(content.plugin_list)
        verbosity = parsers._get_verbosity(args)
        level = 'advanced' if args.all else content.disp_level
        datasets = True if args.datasets else False
        content.display(formatter, level=level, verbose=verbosity,
                        datasets=datasets, **range_dict)
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

    # Sort the list of dictionaries.
    # Sort by the name of the plugin within each dictionary.
    list_content.plugin_list.plugin_list = \
        sorted(list_content.plugin_list.plugin_list,
                key=lambda i: i['name'])

    formatter = ListDisplay(list_content.plugin_list)
    verbosity = parsers._get_verbosity(args)
    list_content.display(formatter, verbose=verbosity)
    return content

@parse_args
@error_catcher
def _save(content, args):
    """ Save the current process list to file."""

    # Check if the plug in list has been populated.
    if len(content.plugin_list.plugin_list) > 0:
        # Check if a loader and saver are present.
        content.plugin_list._check_loaders()
        out_file = content.filename if args.input else args.filepath
        content.check_file(out_file)
        print()
        DispDisplay(content.plugin_list)._notices()
        content.save(out_file, check=input("Are you sure you want to save the "
                     "current data to %s' [y/N]" % (out_file)),
                     template=args.template)
    else:
        raise Exception("No items were found in your process list. "
                    "Type 'add' to add a plugin to the list.")
    return content


@parse_args
@error_catcher
def _mod(content, args):
    """ Modify plugin parameters. """
    try:
        pos_str, subelem = args.param.split('.')

        # Get the name of the modified parameter so that the display
        # lists the correct item when the parameter order has been updated
        plugin_position = content.find_position(pos_str)
        current_parameter_list = \
            content.plugin_list.plugin_list[plugin_position]["param"]
        current_parameter_list_ordered = \
            pu.set_order_by_visibility(current_parameter_list)
        param_name = pu.param_to_str(subelem, current_parameter_list_ordered)

        try:
            content_modified = content.modify(pos_str, subelem, ' '.join(args.value))
            if content_modified:
                # Use the param_name str instead of a number, as after the
                # modification new dependent parameter may appear inside the list
                # and mean the parameter has moved
                args.param = pos_str + '.' + param_name
                _disp(content, str(args.param))
        except Exception:
            print('Error modifying the parameter.')
            raise

    except ValueError:
        print('Incorrect parameter number: Please enter the parameter number to'
              ' select the parameter you want to modify. Use a decimal format.')
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
def _cite(content, args):
    """ Display plugin citations."""
    range_dict = content.get_start_stop(content, args.start, args.stop)
    formatter = CiteDisplay(content.plugin_list)
    content.display(formatter, **range_dict)
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

@parse_args
@error_catcher
def _clear(content, arg):
    """ Clear the current plugin list."""
    content.clear(check=input("Are you sure you want to clear the current "
                  "plugin list? [y/N]"))
    return content

@parse_args
@error_catcher
def _exit(content, arg):
    """ Close the program."""
    content.set_finished(check=input("Are you sure? [y/N]"))
    return content

@parse_args
@error_catcher
def _level(content, args):
    """ Set a visibility level for the parameters."""
    content.level(args.level)
    print(f"Level set to '{args.level}'")
    return content

@parse_args
@error_catcher
def _history(content, arg):
    """ View the history of previous commands """
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
            'cite': _cite,
            'coll': _coll,
            'clear': _clear,
            'exit': _exit,
            'level': _level,
            'history': _history}

def get_description():
    """ For each command, enter the function and save the docstring to a
    dictionary
    """
    command_desc_dict = {command: function_name.__doc__
                         for command, function_name in commands.items()}
    return command_desc_dict

def main(test=False):
    """
    :param test: If test is True the last argument from sys.argv is removed,
                 as it contains the directory of the test scripts, which fails the
                 parsing of the arguments as it has an unexpected argument.

                 If test is False then nothing is touched.
    """

    print("Running the configurator")
    # required for running the tests locally or on travis
    # drops the last argument from pytest which is the test file/module
    if test:
        try:
            # find where the /scripts argument is
            index_of_scripts_argument = ["scripts" in arg for arg in sys.argv].index(True)
            # remove it, including every arguments after it (e.g --cov)
            sys.argv = sys.argv[:index_of_scripts_argument]
        except ValueError:
            # scripts was not part of the arguments passed in by the test
            pass

    args = parsers._config_arg_parser(doc=False)
    if args.error:
        utils.error_level = 1

    print("Starting Savu Config tool (please wait for prompt)")

    _reduce_logging_level()

    content = Content(level="advanced" if args.disp_all else 'basic')

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # imports all the (working) plugin modules
        content.failed = utils.populate_plugins(error_mode=args.error,
                                                examples=args.examples)

    comp = Completer(commands=commands, plugin_list=pu.plugins)
    utils._set_readline(comp.complete)


    # if file flag is passed then open it here
    if args.file:
        commands['open'](content, args.file)

    print("\n*** Press Enter for a list of available commands. ***\n")

    utils.load_history_file(utils.histfile)
    accumulative_output = ''
    while True:
        try:
            in_text = input(">>> ").strip()
            in_list = in_text.split(' ', 1)
            _write_command_to_log(in_text)

        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            # makes possible exiting on CTRL + D (EOF, like Python interpreter)
            break

        command, arg = in_list if len(in_list) == 2 else in_list+['']
        command = command if command else 'help'
        if command not in commands:
            print("I'm sorry, that's not a command I recognise. Press Enter "
                  "for a list of available commands.")
        else:
            content = commands[command](content, arg)
            if logger.handlers:
                # Write the command output to a logger
                accumulative_output = _write_output_to_log(accumulative_output)

        if content.is_finished():
            break

    print("Thanks for using the application")


def _write_command_to_log(in_text):
    logger.debug('TEST COMMAND: ' + in_text)
    block_text = _log_file_code('bash')
    logger_rst.debug(block_text + pu.indent('>>> ' + in_text))


def _write_output_to_log(accumulative_output):
    """ Seperate the current command output, format it correctly
    and write this to the restructured text log file.

    :param accumulative_output:
    :return: accumulative_output
    """
    current_output = sys.stdout.getvalue()

    # Find all previous command output
    length_Str = len(accumulative_output)
    if length_Str:
        # If there is previous output, then select only new lines from the
        # current command. This will demonstrate clearly the output of each
        # individual command
        current_output = current_output[length_Str:]

    # Characters used for command line colour
    unicode_chars = [u'\x1b[100m', u'\x1b[0m', u'\x1b[97m',
                     u'\x1b[49m', u'\x1b[46m', u'\x1b[39m',
                     u'\x1b[36m']
    # Remove unicode characters which cannot be displayed
    for code in unicode_chars:
        current_output = current_output.replace(code, '')

    # Indent the text for the rst file format
    indent_current_output = pu.indent_multi_line_str(current_output)
    # Write to the rst log file
    logger_rst.debug(indent_current_output)
    return sys.stdout.getvalue()


def _log_file_code(type):
    block_text = '''.. code-block:: '''+str(type)+'''

'''
    return block_text


def _reduce_logging_level():
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)

if __name__ == '__main__':
    main()
