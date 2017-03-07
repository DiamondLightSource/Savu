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
import sys


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


def __arg_parser(parser, args):
    try:
        args = parser.parse_args(args=args)
    except MyException as e:
        if e.message:
            print (e.message)
        args = e.args
    return args


def _config_arg_parser():
    """ Argument parser for command line arguments. """
    desc = "Create process lists of plugins for Savu."
    parser = ArgumentParser(prog='savu_config.py', description=desc)
    disp_str = "Set the display level to show ALL parameters by default."
    parser.add_argument("-a", "--all", action="store_true", dest="disp_all",
                        help=disp_str, default=False)
    input_str = "Open a Savu process list."
    parser.add_argument("-i", "--input", dest="input_file", help=input_str)
    return __arg_parser(parser, sys.argv[1:])


def __verbosity_arguments(parser, q_str, v_str, vv_str):
    """ Add verbosity arguments to a parser. """
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        help="Quiet mode. "+q_str, default=False)
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                        help="Verbose mode. "+v_str, default=False)
    parser.add_argument("-vv", "--vverbose", action="store_true",
                        dest="vverbose", help="Verbose verbose mode. "+vv_str,
                        default=False)


def _open_arg_parser(args, desc):
    """ Argument parser for open command. """
    parser = ArgumentParser(prog='add', description=desc)
    file_str = "The path to the process list to open."
    parser.add_argument('file', help=file_str)
    return __arg_parser(parser, args)


#def _disp_arg_parser(args, desc):
#    """ Argument parser for disp command. """
#    parser = ArgumentParser(prog='disp', description=desc)
#    q_str = "Display plugin names only."
#    v_str = "Display plugin names, synopsis and parameter details."
#    vv_str = \
#        "Display plugin names, full synopsis, parameter details and warnings."
#    __verbosity_arguments(parser, q_str, v_str, vv_str)
#
#    all_str = "Display ALL parameters (user parameters only by default)."
#    parser.add_argument("-a", "--all", action='store_true', help=all_str,
#                        default=False)
#
#    ith_str = "Display the ith item in the list 'disp i' OR display items i \
#               to j, 'disp i j'."
#    parser.add_argument("range", nargs='*', help=ith_str, default=[0, -1])
#
#    return __arg_parser(parser, args)
def _disp_arg_parser(args, desc):
    """ Argument parser for disp command. """
    parser = ArgumentParser(prog='disp', description=desc)
    q_str = "Display plugin names only."
    v_str = "Display plugin names, synopsis and parameter details."
    vv_str = \
        "Display plugin names, full synopsis, parameter details and warnings."
    __verbosity_arguments(parser, q_str, v_str, vv_str)

    all_str = "Display ALL parameters (user parameters only by default)."
    parser.add_argument("-a", "--all", action='store_true', help=all_str,
                        default=False)

    parser.add_argument("start", nargs='?', help="Display this list entry.")
    stop_str = "Display entries from start to stop."
    parser.add_argument("stop", nargs='?', help=stop_str)
    return __arg_parser(parser, args)


def _list_arg_parser(args, desc):
    """ Argument parser for list command. """
    parser = ArgumentParser(prog='list', description=desc)
    q_str = "List plugin names only."
    v_str = "List plugin names and full synopsis."
    vv_str = "List all information."
    __verbosity_arguments(parser, q_str, v_str, vv_str)
    type_str = "List plugins or collections containing this string."
    parser.add_argument("string", nargs='?', help=type_str, default="")

    return __arg_parser(parser, args)


def _mod_arg_parser(args, desc):
    """ Argument parser for mod command. """
    parser = ArgumentParser(prog='mod', description=desc)
    param_str = ("The plugin parameter to modify. Either "
                 "'plugin_pos.param_name' or ' plugin_pos.param_no'")
    parser.add_argument("param", help=param_str)
    val_str = ("The plugin parameter value.")
    parser.add_argument("param", help=val_str)
    return __arg_parser(parser, args)


def _set_arg_parser(args, desc):
    """ Argument parser for set command. """
    parser = ArgumentParser(prog='mod', description=desc)
    parser.add_argument('plugin_pos', type=int, help="Plugin position.")
    parser.add_argument("status", type=str, choices=['on', 'ON', 'off', 'OFF'],
                        help="Plugin status (ON of OFF).")
    return __arg_parser(parser, args)


def _add_arg_parser(args, desc):
    """ Argument parser for add command. """
    parser = ArgumentParser(prog='add', description=desc)
    parser.add_argument("name", help="The plugin name.")
    pos_str = "Plugin list position (defaults to end)."
    parser.add_argument('pos', nargs='?', help=pos_str)
    return __arg_parser(parser, args)


def _ref_arg_parser(args, desc):
    """ Argument parser for ref command. """
    parser = ArgumentParser(prog='ref', description=desc)
    plugin_str = "Plugin position to refresh or '*' for the whole list"
    parser.add_argument("pos", nargs='+', help=plugin_str)
    defaults_str = "Populate parameters with default values."
    parser.add_argument("-d", "--defaults", action="store_true",
                        dest="defaults", help=defaults_str, default=False)


def _rem_arg_parser(args, desc):
    """ Argument parser for rem command. """
    parser = ArgumentParser(prog='rem', description=desc)
    parser.add_argument('pos', nargs='+', help="Plugin position(s).")


def _move_arg_parser(args, desc):
    """ Argument parser for move command. """
    parser = ArgumentParser(prog='move', description=desc)
    parser.add_argument("orig_pos", help="Original position.")
    parser.add_argument('new_pos', help="New position.")


def _coll_arg_parser(args, desc):
    """ Argument parser for coll command. """
    parser = ArgumentParser(prog='coll', description=desc)
    return __arg_parser(parser, args)


def _get_verbosity(args):
    if args.vverbose:
        return '-vv'
    elif args.verbose:
        return '-v'
    elif args.quiet:
        return '-q'
    else:
        return None
