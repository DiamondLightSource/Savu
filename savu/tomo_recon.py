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
.. module:: tomo_recon
   :platform: Unix
   :synopsis: Runner for the Savu framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import tempfile  # this import is required for pyFAI - DO NOT REMOVE!
import argparse
import traceback
import sys
import os
from mpi4py import MPI
from savu.version import __version__

from savu.core.plugin_runner import PluginRunner


def __option_parser():
    """ Option parser for command line arguments.
    """
    version = "%(prog)s " + __version__
    parser = argparse.ArgumentParser(prog='savu')
    hide = argparse.SUPPRESS

    parser.add_argument('in_file', help='Input data file.')
    process_str = 'Process list, created with the savu configurator.'
    parser.add_argument('process_list', help=process_str)
    parser.add_argument('out_folder', help='Output folder.')
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument("-f", "--folder", help="Override output folder name")
    tmp_help = "Store intermediate files in a temp directory."
    parser.add_argument("-d", "--tmp", help=tmp_help)
    log_help = "Store full log file in a separate location"
    parser.add_argument("-l", "--log", help=log_help)
    v_help = "Display all debug log messages"
    parser.add_argument("-v", "--verbose", help=v_help, action="store_true",
                        default=False)
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        help="Display only Errors and Info.", default=False)

    # Hidden arguments
    # process names
    parser.add_argument("-n", "--names", help=hide, default="CPU0")
    # transport mechanism
    parser.add_argument("-t", "--transport", help=hide, default="hdf5")
    # Set logging to cluster mode
    parser.add_argument("-c", "--cluster", action="store_true", help=hide,
                        default=False)
    # Location of syslog server
    parser.add_argument("-s", "--syslog", dest="syslog", help=hide,
                        default='localhost')
    # Port to connect to syslog server on
    parser.add_argument("-p", "--syslog_port", dest="syslog_port",
                        help=hide, default=514)
    return parser.parse_args()


def _set_options(args):
    """ Set run specific information in options dictionary.

    :params dict opt: input optional arguments (or defaults)
    :params args: input required arguments
    :returns options: optional and required arguments
    :rtype: dict
    """
    options = {}
    options['data_file'] = args.in_file
    options['process_file'] = args.process_list
    options['transport'] = args.transport
    options['process_names'] = args.names
    options['verbose'] = args.verbose
    options['quiet'] = args.quiet
    options['cluster'] = args.cluster
    options['syslog_server'] = args.syslog
    options['syslog_port'] = args.syslog_port

    out_folder_name = \
        args.folder if args.folder else __get_folder_name(options['data_file'])
    out_folder_path = __create_output_folder(args.out_folder, out_folder_name)

    options['out_folder'] = out_folder_name
    options['out_path'] = out_folder_path
    options['datafile_name'] = os.path.splitext(
            os.path.basename(args.in_file))[0]

    inter_folder_path = __create_output_folder(args.tmp, out_folder_name)\
        if args.tmp else out_folder_path
    options['inter_path'] = inter_folder_path

    options['log_path'] = args.log if args.log else options['inter_path']
    options['nProcesses'] = len(options["process_names"].split(','))

    return options


def __get_folder_name(in_file):
    import time
    MPI.COMM_WORLD.barrier()
    timestamp = time.strftime("%Y%m%d%H%M%S")
    MPI.COMM_WORLD.barrier()
    split = in_file.split('.')

    if len(split[-1].split('/')) > 1:
        split = in_file.split('/')
        name = split[-2] if split[-1] == '' else split[-1]
    # if the input is a file
    else:
        name = os.path.basename(split[-2])
    return '_'.join([timestamp, name])


def __create_output_folder(path, folder_name):
    folder = os.path.join(path, folder_name)
    if MPI.COMM_WORLD.rank == 0:
        if not os.path.exists(folder):
            os.makedirs(folder)
    return folder


def main(input_args=None):
    args = __option_parser()

    if input_args:
        args = input_args

    options = _set_options(args)

    if options['nProcesses'] == 1:
        plugin_runner = PluginRunner(options)
        plugin_runner._run_plugin_list()
    else:
        try:
            plugin_runner = PluginRunner(options)
            plugin_runner._run_plugin_list()
        except Exception as error:
            print error.message
            traceback.print_exc(file=sys.stdout)
            MPI.COMM_WORLD.Abort(1)


if __name__ == '__main__':
    main()
