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
.. module:: mpi_runner
   :platform: Unix
   :synopsis: runner for tests using the MPI framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
# First to pick up the DLS controls environment and versioned libraries
from pkg_resources import require
require('mpi4py==1.3.1')
require('h5py==2.2.0')
require('numpy')  # h5py need to be able to import numpy
require('scipy')

import logging
import optparse
import socket
import tempfile

from mpi4py import MPI
from savu.core import process

import savu.plugins.utils as pu
import savu.test.test_utils as tu

if __name__ == '__main__':

    usage = "%prog [options]"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-n", "--names", dest="names", help="Process names",
                      default="CPU1,CPU2,CPU3,CPU4,CPU5,CPU6,CPU7,CPU8",
                      type='string')
    parser.add_option("-p", "--plugins", dest="plugins",
                      help="List of plugins to run, comma seperated",
                      default="savu.plugins.timeseries_field_corrections",
                      type='string')
    parser.add_option("-d", "--dir", dest="directory",
                      help="Temp direcotry name",
                      default="/dls/tmp/ssg37927/cluster",
                      type='string')
    (options, args) = parser.parse_args()

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
    ALL_PROCESSES = []
    for i in range(MACHINES):
        ALL_PROCESSES.extend(RANK_NAMES)

    logging.basicConfig(level=0, format='L %(asctime)s.%(msecs)03d M' +
                        MACHINE_NUMBER_STRING + ' ' + MACHINE_RANK_NAME +
                        ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

    logging.info(RANK_NAMES)
    logging.info(ALL_PROCESSES)

    plugin_list = options.plugins.split(',')

    MPI.COMM_WORLD.barrier()

    logging.info("Starting the test process")

    IP = socket.gethostbyname(socket.gethostname())

    logging.debug("ip address is : %s", IP)

    MPI.COMM_WORLD.barrier()

    global_data = None

    if RANK == 0:
        temp_file = tempfile.NamedTemporaryFile(dir=options.directory,
                                                suffix='.h5', delete=False)
        logging.debug("Created output file name is  : %s", temp_file.name)
        global_data = {'file_name': temp_file.name}

        logging.debug("Plugin List is:")
        logging.debug(plugin_list)

    global_data = MPI.COMM_WORLD.bcast(global_data, root=0)

    logging.debug("Output file name is  : %s", global_data['file_name'])

    logging.debug("Loading first plugin %s", plugin_list[0])
    first_plugin = pu.load_plugin(None, plugin_list[0])
    logging.debug("Getting input data")
    input_data = tu.get_appropriate_input_data(first_plugin)[0]
    logging.debug("Running plugin chain")
    process.run_plugin_chain(input_data, plugin_list, options.directory,
                             mpi=True, processes=ALL_PROCESSES,
                             process=RANK)

    MPI.COMM_WORLD.barrier()
