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
.. module:: savu_mod
   :platform: Unix
   :synopsis: A command line tool for editing process lists

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""

import os
import argparse
from datetime import datetime

from scripts.config_generator.config_utils import error_catcher_savu

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import scripts.config_generator.savu_config as sc
    from scripts.config_generator.content import Content
    from scripts.config_generator.display_formatter import DispDisplay

def arg_parser(doc=True):
    """ Arg parser for command line arguments.
    """
    desc = "Modify one parameter value inside one process list."
    parser = argparse.ArgumentParser(prog='savu_mod', description=desc)
    parser.add_argument('plugin',
                        help='Plugin name or number',
                        type=str)
    parser.add_argument('plugin_index',
                        help='Associated plugin index (for when identical plugins are present in the process list)',
                        nargs="?", type=int, default=1)
    parser.add_argument('param',
                        help='Parameter name or number from the list of plugin parameters',
                        type=str)
    parser.add_argument("value", help="New parameter value")
    parser.add_argument('process_list',
                        help='Process list file path',
                        type=str)
    save_str = "Save the modified process list without a confirmation."
    parser.add_argument("-q", "--quick", action="store_true",
                        dest="save", help=save_str, default=False)
    copy_str = "Save the modified process list to the same location, " \
               "with a timestamp appended to the name."
    parser.add_argument("-c", "--copy", action="store_true",
                        dest="copy", help=copy_str, default=False)
    return parser if doc is True else parser.parse_args()


def load_process_list(process_list):
    """ Load only plugins inside the process list to the configurator"""
    content = Content(level='basic')
    # Open the process list file
    content.fopen(process_list, update=True)
    # Refresh the plugins
    sc._ref(content, '* -n')
    return content

def timestamp_file(filename):
    """ Return a filename with a timestamp

    :param filename: filename input
    :return: t_filename, the filename with a timestamp
    """
    cur_time = datetime.now().strftime("%Y_%m_%d-%H:%M:%S:%f")
    filelist = filename.split(".")
    t_filename = f"{filelist[0]}_{cur_time}.{filelist[1]}"
    return t_filename

def modify_content(args):
    """Load the process list and modify the parameter value.
    (The savu_config function isn't accessed directly as the
    arg parser takes different arguments)
    """
    if not os.path.isfile(args.process_list):
        raise ValueError("Please enter a valid directory.")

    content = load_process_list(args.process_list)
    # Modify the plugin and parameter value
    plugin = content.plugin_to_num(args.plugin, args.plugin_index)
    content_modified = content.modify(plugin, args.param, args.value)

    return content, content_modified


def save_content(content, args):
    """Save the plugin list with the modified parameter value """
    content.check_file(args.process_list)
    DispDisplay(content.plugin_list)._notices()
    filename = timestamp_file(args.process_list) \
               if args.copy else args.process_list
    save_file = "y" if args.save else input("Are you sure you want to save "
        "the modified process list to %s [y/N]" % (filename))
    content.save(filename, check=save_file)


@error_catcher_savu
def command_line_modify():
    """ Allows modification of one parameter from one plugin.
    Aims to allow easier modification when performing batch processing
    and applying the same process lists to multiple data sets, with
    minor adjustments
    """
    args = arg_parser(doc=False)

    content, content_modified = modify_content(args)
    if content_modified:
        print(f"Parameter {args.param} for the plugin {args.plugin} was "
              f"modified to {args.value}.")
        save_content(content, args)


if __name__ == '__main__':
    command_line_modify()

