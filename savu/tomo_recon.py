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
import optparse
import sys
import os

from savu.core.plugin_runner import PluginRunner


def __option_parser():
    """ Option parser for command line arguments.
    """
    usage = "%prog [options] input_file processing_file output_directory"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-n", "--names", dest="names", help="Process names",
                      default="CPU0")
    parser.add_option("-t", "--transport", dest="transport",
                      help="Set the transport mechanism", default="hdf5")
    parser.add_option("-f", "--folder", dest="folder",
                      help="Override the output folder")
    parser.add_option("-d", "--tmp", dest="temp_dir",
                      help="Store intermediate files in a temp directory.")
    parser.add_option("-l", "--log", dest="log_dir",
                      help="Store log files in a separate location")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Display all debug log messages", default=False)
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
                      help="Display only Errors and Info", default=False)
    #  add -s 'cs04r-sc-serv-14' to module file
    parser.add_option("-s", "--syslog", dest="syslog",
                      help="Location of syslog server",
                      default='localhost')
    parser.add_option("-p", "--syslog_port", dest="syslog_port",
                      help="Port to connect to syslog server on", default=514)

    (options, args) = parser.parse_args()
    return [options, args]


def __check_input_params(args):
    """ Check for required input arguments.
    """
    if len(args) is not 3:
        print("filename, process file and output path needs to be specified")
        print("Exiting with error code 1 - incorrect number of inputs")
        sys.exit(1)

    if not os.path.exists(args[0]):
        print("Input file '%s' does not exist" % args[0])
        print("Exiting with error code 2 - Input file missing")
        sys.exit(2)

    if not os.path.exists(args[1]):
        print("Processing file '%s' does not exist" % args[1])
        print("Exiting with error code 3 - Processing file missing")
        sys.exit(3)

    if not os.path.exists(args[2]):
        print("Output Directory '%s' does not exist" % args[2])
        print("Exiting with error code 4 - Output Directory missing")
        sys.exit(4)


def _set_options(opt, args):
    """ Set run specific information in options dictionary.

    :params dict opt: input optional arguments (or defaults)
    :params args: input required arguments
    :returns options: optional and required arguments
    :rtype: dict
    """
    options = {}
    options["transport"] = opt.transport
    options["process_names"] = opt.names
    options["verbose"] = opt.verbose
    options["quiet"] = opt.quiet
    options["data_file"] = args[0]
    options["process_file"] = args[1]
    options["out_path"] = set_output_folder(args[0], args[2], opt.folder)

    if opt.temp_dir:
        options["inter_path"] = opt.temp_dir
    else:
        options["inter_path"] = options["out_path"]
    if opt.log_dir:
        options['log_path'] = opt.log_dir
    else:
        options['log_path'] = options["out_path"]
    options['syslog_server'] = opt.syslog
    options['syslog_port'] = opt.syslog_port
    return options


def set_output_folder(in_file, out_path, set_folder):
    from mpi4py import MPI

#    # temporarily outputting environment variables
#    rank = MPI.COMM_WORLD.rank
#    filename = out_path + "/envs_" + str(rank)
#    fid = open(filename, 'w')
#    fid.write(str(os.environ))
#    fid.close()

    import time
    if not set_folder:
        MPI.COMM_WORLD.barrier()
        timestamp = time.strftime("%Y%m%d%H%M%S")
        MPI.COMM_WORLD.barrier()
        split = in_file.split('.')
        if split[-1] != 'nxs':
            split = in_file.split('/')
            name = split[-2] if split[-1] == '' else split[-1]
        else:
            name = os.path.basename(split[-2])
        folder = os.path.join(out_path, ('_'.join([timestamp, name])))
    else:
        folder = os.path.join(out_path, set_folder)
    if MPI.COMM_WORLD.rank == 0:
        if not os.path.exists(folder):
            os.makedirs(folder)
    return folder


def main(input_args=None):
    [options, args] = __option_parser()

    if input_args:
        args = input_args

    __check_input_params(args)

    options = _set_options(options, args)
    plugin_runner = PluginRunner(options)
    plugin_runner._run_plugin_list()

if __name__ == '__main__':
    main()
