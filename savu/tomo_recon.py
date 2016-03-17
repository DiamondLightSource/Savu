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
   :synopsis: runner for tests using the MPI framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import optparse
import sys
import os

from savu.core.plugin_runner import PluginRunner


def option_parser():
    usage = "%prog [options] input_file processing_file output_directory"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-n", "--names", dest="names", help="Process names",
                      default="CPU0",
                      type='string')
    parser.add_option("-t", "--transport", dest="transport",
                      help="Set the transport mechanism",
                      default="hdf5",
                      type='string')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Display all debug log messages", default=False)
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
                      help="Display only Errors and Info", default=False)

    (options, args) = parser.parse_args()
    return [options, args]


def check_input_params(args):
    # Check basic items for completeness
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


def set_options(opt, args):
    options = {}
    options["transport"] = opt.transport
    options["process_names"] = opt.names
    options["verbose"] = opt.verbose
    options["quiet"] = opt.quiet
    options["data_file"] = args[0]
    options["process_file"] = args[1]
    options["out_path"] = args[2]
    return options

def main():
    [options, args] = option_parser()
    check_input_params(args)
    options = set_options(options, args)
    plugin_runner = PluginRunner(options)
    plugin_runner._run_plugin_list(options)

    
if __name__ == '__main__':
    main()