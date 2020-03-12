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


def __arg_parser(parser, args, command):
    try:
        args = parser.parse_args(args=args)
    except MyException as e:
        print(e)
        print(f"Please type '{command} -h' for help.")
        args = e.args
    return args


def _config_arg_parser():
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
    return parser.parse_args()


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
    parser = ArgumentParser(prog='open', description=desc)
    file_str = "The path to the process list to open."
    parser.add_argument('file', help=file_str)
    parser.add_argument('-s', '--skip', help='Skip broken plugins.',
                        action='store_true', default=False)
    return __arg_parser(parser, args, 'open')


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
    return __arg_parser(parser, args, 'disp')


def _list_arg_parser(args, desc):
    """ Argument parser for list command. """
    parser = ArgumentParser(prog='list', description=desc)
    q_str = "List plugin names only."
    v_str = "List plugin names and full synopsis."
    vv_str = "List all information."
    __verbosity_arguments(parser, q_str, v_str, vv_str)
    type_str = "List plugins or collections containing this string."
    parser.add_argument("string", nargs='?', help=type_str, default="")

    return __arg_parser(parser, args, 'list')


def _save_arg_parser(args, desc):
    """ Argument parser for save command. """
    parser = ArgumentParser(prog='save', description=desc)
    parser.add_argument("filepath", nargs='?', help="The output file path.")
    parser.add_argument("-i", "--input", action="store_true", default=False,
                        help="Save to the input file.")
    parser.add_argument("-t", "--template", action="store_true", default=False,
                        help="Create a Savu template file.")
    return __arg_parser(parser, args, 'save')


def _mod_arg_parser(args, desc):
    """ Argument parser for mod command. """
    # required to allow negative values in a list or tuple
    args.insert(1, '--')

    parser = ArgumentParser(prog='mod', description=desc)
    param_str = ("The plugin parameter to modify. Either "
                 "'plugin_pos.param_name' or ' plugin_pos.param_no'")
    parser.add_argument("param", help=param_str)
    val_str = "The plugin parameter value."
    parser.add_argument("value", nargs='+', help=val_str)
    return __arg_parser(parser, args, 'mod')


def _set_arg_parser(args, desc):
    """ Argument parser for set command. """
    parser = ArgumentParser(prog='set', description=desc)
    parser.add_argument('plugin_pos', type=str, nargs='+',
                        help="Plugin position.")
    parser.add_argument("status", type=str, choices=['on', 'ON', 'off', 'OFF'],
                        help="Plugin status.")
    return __arg_parser(parser, args, 'set')


def _add_arg_parser(args, desc):
    """ Argument parser for add command. """
    parser = ArgumentParser(prog='add', description=desc)
    parser.add_argument("name", help="The plugin name.")
    pos_str = "Plugin list position (defaults to end)."
    parser.add_argument('pos', nargs='?', help=pos_str)
    return __arg_parser(parser, args, 'add')


def _ref_arg_parser(args, desc):
    """ Argument parser for ref command. """
    parser = ArgumentParser(prog='ref', description=desc)
    plugin_str = "Plugin position to refresh or '*' for the whole list"
    parser.add_argument("pos", nargs='+', help=plugin_str)
    defaults_str = "Populate parameters with default values."
    parser.add_argument("-d", "--defaults", action="store_true",
                        dest="defaults", help=defaults_str, default=False)
    parser.add_argument("-n", "--nodisp", action="store_true", dest="nodisp",
                        help=argparse.SUPPRESS, default=False)
    return __arg_parser(parser, args, 'ref')


def _rem_arg_parser(args, desc):
    """ Argument parser for rem command. """
    parser = ArgumentParser(prog='rem', description=desc)
    parser.add_argument('pos', help="Plugin position(s).")
    return __arg_parser(parser, args, 'rem')


def _move_arg_parser(args, desc):
    """ Argument parser for move command. """
    parser = ArgumentParser(prog='move', description=desc)
    parser.add_argument("orig_pos", help="Original position.")
    parser.add_argument('new_pos', help="New position.")
    return __arg_parser(parser, args, 'move')


def _coll_arg_parser(args, desc):
    """ Argument parser for coll command. """
    parser = ArgumentParser(prog='coll', description=desc)
    return __arg_parser(parser, args, 'coll')


def _get_verbosity(args):
    if args.vverbose:
        return '-vv'
    elif args.verbose:
        return '-v'
    elif args.quiet:
        return '-q'
    else:
        return None
