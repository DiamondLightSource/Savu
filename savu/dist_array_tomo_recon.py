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
   :synopsis: runner for tests using the different transport mechanisms

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import logging
import optparse
import sys
import os

from savu.data.plugin_info import PluginList

MACHINE_NUMBER_STRING = '0'
MACHINE_RANK_NAME = 'cpu1'

if __name__ == '__main__':

    usage = "%prog [options] input_file output_directory"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-n", "--names", dest="names", help="Process names",
                      default="CPU1,CPU2,CPU3,CPU4,CPU5,CPU6,CPU7,CPU8",
                      type='string')
    parser.add_option("-f", "--filename", dest="process_filename",
                      help="The filename of the process file",
                      default=  + "/test_data/process01.nxs",
                      type='string')
    parser.add_option("-t", "--transport", dest="transport_str",
                      help="Set the transport mechanism",
                      default="hdf5",
                      type='string')
    (options, args) = parser.parse_args()


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

    # set up logging 
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(os.path.join(args[2],'log.txt'), mode='w')
    fh.setFormatter(logging.Formatter('L %(relativeCreated)12d M' +
            MACHINE_NUMBER_STRING + ' ' + MACHINE_RANK_NAME +
            ' %(levelname)-6s %(message)s'))
    logger.addHandler(fh)

    logging.info("Starting tomo_recon process")

    # set up transport
    if options.transport_str is "hdf5":
        from savu.data.transports.hdf5_transport import Hdf5Transport as Transport
    elif options.transport_str is "distArray":
        from savu.data.transports.dist_array_transport import dist_array_transport as Transport
    else:
        print("The transport mechanism", options.transport_str, "is not recognised")
        print("Exiting with error code 5 - Unrecognised transport mechanism")
        sys.exit(5)
    
    plugin_list = PluginList()
    plugin_list.populate_plugin_list(options.process_filename)
    transport = Transport()
    transport.run_plugin_list(args[0], plugin_list, args[2])
    