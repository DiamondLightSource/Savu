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
.. module:: arg_parsers
   :platform: Unix
   :synopsis: Contains all the argparse instances for configurator \
       input commands.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import argparse

from . import savu_config as sc


class MyException(Exception):
    def __init__(self, message, args=None):
        super(MyException, self).__init__(message)
        self.args = args

    def args(self):
        return self.args


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        raise MyException(message)

    def exit(self, status=0, message=None):
        raise MyException(message)


def __arg_parser(parser, args, command, doc):
    try:
        args = parser.parse_args(args=args)
    except MyException as e:
        args = e.args
        if args is not None:
            print(e)
        print(f"Please type '{command} -h' for help.")
    return parser if doc==True else args


def _config_arg_parser(doc=True):
    """ Argument parser for command line arguments. """
    desc = "Create process lists of plugins for Savu."
    parser = argparse.ArgumentParser(prog='savu_config.py', description=desc)
    disp_str = "Set the display level to show ALL parameters by default."
    parser.add_argument("-a", "--all", action="store_true", dest="disp_all",
                        help=disp_str, default=False)
    input_str = "Open a Savu process list."
    parser.add_argument("-i", "--input", dest="file", help=input_str)
    parser.add_argument("-e", "--error", dest="error", help="Shows all errors that Savu encounters.",
                        action='store_true', default=False)
    parser.add_argument("--examples", dest="examples", action='store_true',
                        help="Add example plugins", default=False)
    return parser if doc==True else parser.parse_args()


def __verbosity_arguments(parser, q_str, v_str, vv_str):
    """ Add verbosity arguments to a parser. """
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        help="Quiet mode. "+q_str, default=False)
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                        help="Verbose mode. "+v_str, default=False)
    parser.add_argument("-vv", "--vverbose", action="store_true",
                        dest="vverbose", help="Verbose verbose mode. "+vv_str,
                        default=False)


def _open_arg_parser(args=None, doc=True):
    """ Argument parser for open command. """
    desc = sc.get_description()['open']
    parser = ArgumentParser(prog='open', description=desc)
    file_str = "The path to the process list to open."
    parser.add_argument('file', help=file_str)
    parser.add_argument('-s', '--skip', help='Skip broken plugins.',
                        action='store_true', default=False)
    return __arg_parser(parser, args, 'open', doc)


def _disp_arg_parser(args=None, doc=True):
    """ Argument parser for disp command. """
    desc = sc.get_description()['disp']
    parser = ArgumentParser(prog='disp', description=desc)
    q_str = "Display plugin names only."
    v_str = "Display plugin names, synopsis and parameter details."
    vv_str = \
        "Display plugin names, full synopsis, parameter details and warnings."
    __verbosity_arguments(parser, q_str, v_str, vv_str)

    all_str = "Display ALL parameters (user parameters only by default)."
    parser.add_argument("-a", "--all", action='store_true', help=all_str,
                        default=False)
    l_str = "Display current parameter visibility level."
    parser.add_argument("-l", "--level", action='store_true', help=l_str,
                        default=False)
    dataset_str = "Display in_datasets and out_datasets."
    parser.add_argument("-d", "--datasets", action='store_true', help=dataset_str,
                        default=False)

    parser.add_argument("start", nargs='?', help="Display this list entry.")
    stop_str = "Display entries from start to stop."
    parser.add_argument("stop", nargs='?', help=stop_str)
    return __arg_parser(parser, args, 'disp', doc)


def _list_arg_parser(args=None, doc=True):
    """ Argument parser for list command. """
    desc = sc.get_description()['list']
    parser = ArgumentParser(prog='list', description=desc)
    q_str = "List plugin names only."
    v_str = "List plugin names and full synopsis."
    vv_str = "List all information."
    __verbosity_arguments(parser, q_str, v_str, vv_str)
    type_str = "List plugins or collections containing this string."
    parser.add_argument("string", nargs='?', help=type_str, default="")
    return __arg_parser(parser, args, 'list', doc)


def _save_arg_parser(args=None, doc=True):
    """ Argument parser for save command. """
    desc = sc.get_description()['save']
    parser = ArgumentParser(prog='save', description=desc)
    parser.add_argument("filepath", nargs='?', help="The output file path.")
    parser.add_argument("-i", "--input", action="store_true", default=False,
                        help="Save to the input file.")
    parser.add_argument("-t", "--template", action="store_true", default=False,
                        help="Create a Savu template file.")
    return __arg_parser(parser, args, 'save', doc)


def _mod_arg_parser(args=None, doc=True):
    """ Argument parser for mod command. """
    # required to allow negative values in a list or tuple
    if args:
        args.insert(1, '--')
    desc = sc.get_description()['mod']
    parser = ArgumentParser(prog='mod', description=desc)
    param_str = ("The plugin parameter to modify. Either "
                 "'plugin_pos.param_name' or ' plugin_pos.param_no'")
    parser.add_argument("param", help=param_str)
    val_str = "The plugin parameter value."
    parser.add_argument("value", nargs='*', help=val_str)
    parser.add_argument("-d", "--default", action="store_true", default=False,
                        help="Revert to default value.")
    return __arg_parser(parser, args, 'mod', doc)


def _set_arg_parser(args=None, doc=True):
    """ Argument parser for set command. """
    desc = sc.get_description()['set']
    parser = ArgumentParser(prog='set', description=desc)
    parser.add_argument('plugin_pos', type=str, nargs='+',
                        help="Plugin position(s).")
    parser.add_argument("status", type=str, choices=['on', 'ON', 'off', 'OFF'],
                        help="Plugin status.")
    return __arg_parser(parser, args, 'set', doc)


def _add_arg_parser(args=None, doc=True):
    """ Argument parser for add command. """
    desc = sc.get_description()['add']
    parser = ArgumentParser(prog='add', description=desc)
    parser.add_argument("name", help="The plugin name.")
    pos_str = "Plugin list position (defaults to end)."
    parser.add_argument('pos', nargs='?', help=pos_str)
    return __arg_parser(parser, args, 'add', doc)


def _dupl_arg_parser(args=None, doc=True):
    """ Argument parser for dupl command. """
    desc = sc.get_description()['dupl']
    parser = ArgumentParser(prog='dupl', description=desc)
    orig_pos_str = "The position of the plugin to be duplicated."
    parser.add_argument("orig_pos", help=orig_pos_str)
    pos_str = "Position for the new plugin (defaults to end)."
    parser.add_argument('new_pos', nargs='?', help=pos_str)
    return __arg_parser(parser, args, 'dupl', doc)


def _ref_arg_parser(args=None, doc=True):
    """ Argument parser for ref command. """
    desc = sc.get_description()['ref']
    parser = ArgumentParser(prog='ref', description=desc)
    plugin_str = "Plugin position to refresh or '*' for the whole list"
    parser.add_argument("pos", nargs='+', help=plugin_str)
    defaults_str = "Populate parameters with default values."
    parser.add_argument("-d", "--defaults", action="store_true",
                        dest="defaults", help=defaults_str, default=False)
    parser.add_argument("-n", "--nodisp", action="store_true", dest="nodisp",
                        help=argparse.SUPPRESS, default=False)
    return __arg_parser(parser, args, 'ref', doc)


def _rem_arg_parser(args=None, doc=True):
    """ Argument parser for rem command. """
    desc = sc.get_description()['rem']
    parser = ArgumentParser(prog='rem', description=desc)
    parser.add_argument('pos', type=str, nargs='+',
                            help="Plugin position(s).")
    return __arg_parser(parser, args, 'rem', doc)


def _cite_arg_parser(args=None, doc=True):
    """ Argument parser for cite command. """
    desc = sc.get_description()['cite']
    parser = ArgumentParser(prog='cite', description=desc)
    parser.add_argument("start", nargs='?', help="Display this plugin citation.")
    stop_str = "Display plugins from start to stop."
    parser.add_argument("stop", nargs='?', help=stop_str)
    return __arg_parser(parser, args, 'cite', doc)


def _move_arg_parser(args=None, doc=True):
    """ Argument parser for move command. """
    desc = sc.get_description()['move']
    parser = ArgumentParser(prog='move', description=desc)
    parser.add_argument("orig_pos", help="Original position.")
    parser.add_argument('new_pos', help="New position.")
    return __arg_parser(parser, args, 'move', doc)


def _coll_arg_parser(args=None, doc=True):
    """ Argument parser for coll command. """
    desc = sc.get_description()['coll']
    parser = ArgumentParser(prog='coll', description=desc)
    return __arg_parser(parser, args, 'coll', doc)


def _level_arg_parser(args=None, doc=True):
    """ Argument parser for level command. """
    desc = sc.get_description()['level']
    parser = ArgumentParser(prog='level', description=desc)
    level_str = "The visibility level. Display the current visibility level" \
                " by using 'level' without an argument."
    parser.add_argument("level",  nargs='?', help=level_str
                        , choices=['basic', 'intermediate', 'advanced'])
    return __arg_parser(parser, args, 'level', doc)


def _expand_arg_parser(args=None, doc=True):
    """ Argument parser for expand command. """
    desc = sc.get_description()["expand"]
    parser = ArgumentParser(prog="expand", description=desc)
    plugin_pos_str = "Expand this plugin preview parameter"
    parser.add_argument("plugin_pos", nargs="?", help=plugin_pos_str)
    dim_str = "Data dimensions. If this value is the same as the " \
              "current dimension value, then the dimension of the " \
              "preview parameter will be unchanged. If it is greater " \
              "or smaller than the current dimension value, then the " \
              "dimension of the preview value will be altered."
    parser.add_argument("dim", nargs="?", type=int, help=dim_str)
    # Hidden argument to use when argument can be string and one
    # dimension is displayed
    parser.add_argument('dim_view', nargs="?", default=False,
                        help=argparse.SUPPRESS)
    expand_off_str = "Turn off the expand view"
    parser.add_argument("--off", action="store_true",
                        dest="off", help=expand_off_str, default=False)
    return __arg_parser(parser, args, "expand", doc)


def _clear_arg_parser(args=None, doc=True):
    """ Argument parser for clear command. """
    desc = sc.get_description()['clear']
    parser = ArgumentParser(prog='clear', description=desc)
    return __arg_parser(parser, args, 'clear', doc)


def _history_arg_parser(args=None, doc=True):
    """ Argument parser for history command. """
    desc = sc.get_description()['history']
    parser = ArgumentParser(prog='history', description=desc)
    return __arg_parser(parser, args, 'history', doc)


def _exit_arg_parser(args=None, doc=True):
    """ Argument parser for exit command """
    desc = sc.get_description()['exit']
    parser = ArgumentParser(prog='exit', description=desc)
    return __arg_parser(parser, args, 'exit', doc)


def _help_arg_parser(args=None, doc=True):
    """ Argument parser for help command """
    desc = sc.get_description()['help']
    parser = ArgumentParser(prog='help', description=desc)
    return __arg_parser(parser, args, 'help', doc)


def _get_verbosity(args):
    if args.vverbose:
        return '-vv'
    elif args.verbose:
        return '-v'
    elif args.quiet:
        return '-q'
    else:
        return None
