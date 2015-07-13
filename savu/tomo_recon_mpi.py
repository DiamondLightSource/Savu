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
.. module:: tomo_recon_mpi
   :platform: Unix
   :synopsis: runner for full reconstruction pilpeline using the MPI framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging
import optparse
import socket
import sys
import os

from itertools import chain
from mpi4py import MPI

from savu.core import process
from savu.data.plugin_info import PluginList
from savu.core.utils import logfunction

import savu.plugins.utils as pu


@logfunction
def call_mpi_barrier():
    logging.debug("Waiting at the barrier")
    MPI.COMM_WORLD.barrier()

if __name__ == '__main__':

    usage = "%prog [options] nxs_file_to_reconstruct process_file output_dir"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-n", "--names", dest="names", help="Process names",
                      default="CPU1,CPU2,CPU3,CPU4,CPU5,CPU6,CPU7,CPU8",
                      type='string')
    (options, args) = parser.parse_args()
    
    # Check basic items for completeness
    if len(args) is not 3:
        print len(args)
        print "filename, process file and output path needs to be specified"
        print "Exiting with error code 1 - incorrect number of inputs"
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

    RANK_NAMES = options.names.split(',')

    RANK = MPI.COMM_WORLD.rank
    SIZE = MPI.COMM_WORLD.size
    RANK_NAMES_SIZE = len(RANK_NAMES)
    if RANK_NAMES_SIZE > SIZE:
        RANK_NAMES_SIZE = SIZE
    MACHINES = SIZE/RANK_NAMES_SIZE
    MACHINE_RANK = RANK/MACHINES
    MACHINE_RANK_NAME = RANK_NAMES[MACHINE_RANK]
    MACHINE_NUMBER = RANK % MACHINES
    MACHINE_NUMBER_STRING = "%03i" % (MACHINE_NUMBER)
    ALL_PROCESSES = [[i]*MACHINES for i in RANK_NAMES]
    ALL_PROCESSES = list(chain.from_iterable(ALL_PROCESSES))

    logging.basicConfig(level=0, format='L %(relativeCreated)12d M' +
                        MACHINE_NUMBER_STRING + ' ' + MACHINE_RANK_NAME +
                        ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

    MPI.COMM_WORLD.barrier()

    logging.info("Starting the reconstruction pipeline process")

    logging.debug("Rank : %i - Size : %i - host : %s", RANK, SIZE, socket.gethostname())

    IP = socket.gethostbyname(socket.gethostname())

    logging.debug("ip address is : %s", IP)

    call_mpi_barrier()
    
    logging.debug("LD_LIBRARY_PATH is %s",  os.getenv('LD_LIBRARY_PATH'))

    call_mpi_barrier()

    process_filename = args[1]

    plugin_list = PluginList()
    plugin_list.populate_process_list(process_filename)

    input_data = pu.load_raw_data(args[0])

    process.run_process_list(input_data, plugin_list, args[2],
                             mpi=True, processes=ALL_PROCESSES,
                             process=RANK)

    call_mpi_barrier()

    logging.info("Python MPI script complete")
