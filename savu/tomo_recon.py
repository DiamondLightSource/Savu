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

import savu.core.utils as cu
from scripts.citation_extractor import citation_extractor
from savu.core.basic_plugin_runner import BasicPluginRunner
from savu.core.plugin_runner import PluginRunner


def __option_parser(doc=True):
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

    template_help = "Pass a template file of plugin input parameters."
    parser.add_argument("-t", "--template", help=template_help, default=None)

    log_help = "Store full log file in a separate location"
    parser.add_argument("-l", "--log", help=log_help)

    v_help = "Display all debug log messages"
    parser.add_argument("-v", "--verbose", help=v_help, action="store_true",
                        default=False)
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        help="Display only Errors and Info.", default=False)
    # temporary flag to fix lustre issue
    parser.add_argument("--lustre_workaround", action="store_true",
                        dest="lustre", help="Avoid lustre segmentation fault",
                        default=False)
    sys_params_help = "Override default path to Savu system parameters file."
    parser.add_argument("--system_params", help=sys_params_help, default=None)

    # Set stats off
    parser.add_argument("--stats", help="Turn stats 'on' or 'off'.", default="on", choices=["on", "off"])

    # Hidden arguments
    # process names
    parser.add_argument("-n", "--names", help=hide, default="CPU0")
    # transport mechanism
    parser.add_argument("--transport", help=hide, default="hdf5")
    # Set Savu mode
    parser.add_argument("-m", "--mode", help=hide, default="full",
                        choices=['basic', 'full'])
    # Set logging to cluster mode
    parser.add_argument("-c", "--cluster", action="store_true", help=hide,
                        default=False)
    # Send an email on completion
    parser.add_argument("-e", "--email", dest="email", help=hide, default=None)
    # Facility email for errors
    parser.add_argument("--facility_email", dest="femail", help=hide,
                        default=None)
    # Set beamline log file (for online processing)
    parser.add_argument("--bllog", dest="bllog", help=hide, default=None)
    # Location of syslog server
    parser.add_argument("-s", "--syslog", dest="syslog", help=hide,
                        default='localhost')
    # Port to connect to syslog server on
    parser.add_argument("-p", "--syslog_port", dest="syslog_port",
                        help=hide, default=514, type=int)
    parser.add_argument("--test_state", dest="test_state", default='False',
                        action='store_true', help=hide)

    # DosNa related parameters
    parser.add_argument("--dosna_backend", dest="dosna_backend", help=hide,
                        default=None)
    parser.add_argument("--dosna_engine", dest="dosna_engine", help=hide,
                        default=None)
    parser.add_argument("--dosna_connection", dest="dosna_connection",
                        help=hide, default=None)
    parser.add_argument("--dosna_connection_options",
                        dest="dosna_connection_options", help=hide,
                        nargs='+', default=[])

    check_help = "Continue Savu processing from a checkpoint."
    choices = ['plugin', 'subplugin']
    parser.add_argument("--checkpoint", nargs="?", choices=choices,
                        const='plugin', help=check_help, default=None)
    if doc==False:
        args = parser.parse_args()
        __check_conditions(parser, args)
        return args
    else:
        return parser


def __check_conditions(parser, args):
    if args.checkpoint and not args.folder:
        msg = "--checkpoint flag requires '-f folder_name', where folder_name"\
              " contains the partially completed Savu job.  The out_folder"\
              " should be the path to this folder."
        parser.error(msg)


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
    options['mode'] = args.mode
    options['template'] = args.template
    options['transport'] = 'basic' if args.mode == 'basic' else args.transport
    options['process_names'] = args.names
    options['verbose'] = args.verbose
    options['quiet'] = args.quiet
    options['cluster'] = args.cluster
    options['syslog_server'] = args.syslog
    options['syslog_port'] = args.syslog_port
    options['test_state'] = args.test_state
    options['lustre'] = args.lustre
    options['bllog'] = args.bllog
    options['email'] = args.email
    options['femail'] = args.femail
    options['system_params'] = args.system_params
    options['stats'] = args.stats

    if args.folder:
        out_folder_name = os.path.basename(args.folder)
    else:
        out_folder_name = __create_folder_name(options['data_file'])

    out_folder_path = __create_output_folder(args.out_folder, out_folder_name)

    options['out_folder'] = out_folder_name
    options['out_path'] = out_folder_path

    basename = os.path.basename(args.in_file)
    options['datafile_name'] = os.path.splitext(basename)[0] if basename \
        else args.in_file.split(os.sep)[-2]

    inter_folder_path = __create_output_folder(args.tmp, out_folder_name)\
        if args.tmp else out_folder_path

    options['inter_path'] = inter_folder_path
    options['log_path'] = args.log if args.log else options['inter_path']
    options['nProcesses'] = len(options["process_names"].split(','))
    # DosNa related options
    options["dosna_backend"] = args.dosna_backend
    options["dosna_engine"] = args.dosna_engine
    options["dosna_connection"] = args.dosna_connection
    options["dosna_connection_options"] = args.dosna_connection_options
    options['checkpoint'] = args.checkpoint

    command_str = " ".join([str(i) for i in sys.argv[1:]])
    command_full = f"savu {command_str}"
    options["command"] = command_full

    return options


def __create_folder_name(dpath):
    if os.path.isfile(dpath):
        dpath = os.path.splitext(dpath)[0]
    elif os.path.isdir(dpath):
        dpath = os.path.dirname(dpath)
    import time
    MPI.COMM_WORLD.barrier()
    timestamp = time.strftime("%Y%m%d%H%M%S")
    MPI.COMM_WORLD.barrier()
    return "_".join([timestamp, os.path.basename(dpath)])


def __create_output_folder(path, folder_name):
    folder = os.path.join(path, folder_name)
    if MPI.COMM_WORLD.rank == 0:
        if not os.path.exists(folder):
            os.makedirs(folder)
    return folder


def main(input_args=None):
    args = __option_parser(doc=False)

    if input_args:
        args = input_args

    options = _set_options(args)
    pRunner = PluginRunner if options['mode'] == 'full' else BasicPluginRunner

    try:
        plugin_runner = pRunner(options)
        plugin_runner._run_plugin_list()
        if options['process'] == 0:
            in_file = plugin_runner.exp.meta_data['nxs_filename']
            citation_extractor.main(in_file=in_file, quiet=True)
    except Exception:
        # raise the error in the user log
        trace = traceback.format_exc()
        cu.user_message(trace)
        if options['nProcesses'] == 1:
            sys.exit(1)
        else:
            # Kill all MPI processes
            MPI.COMM_WORLD.Abort(1)


if __name__ == '__main__':
    main()
