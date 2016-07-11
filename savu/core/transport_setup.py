# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: transport_setup
   :platform: Unix
   :synopsis: Module containing classes required for transport setup, e.g MPI.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import socket
import os

from mpi4py import MPI
from itertools import chain
import savu.core.utils as cu

#
#class logging_setup(object):
#
#    def __init__(self, options, name='logging_setup'):
#        self.options = options
#


class MPI_setup(object):

    def __init__(self, options, name='MPI_setup'):
        self.__set_dictionary(options)

    def __set_dictionary(self, options):
        """ Fill the options dictionary with MPI related values.
        """
        processes = options["process_names"].split(',')

        if len(processes) is 1:
            options["mpi"] = False
            options["process"] = 0
            options["processes"] = processes
            self.__set_logger_single(options)
        else:
            options["mpi"] = True
            self.__mpi_setup(options)

    def __mpi_setup(self, options):
        """ Set MPI process specific values and logging initialisation.
        """
        print("Running mpi_setup")
        RANK_NAMES = options["process_names"].split(',')
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
        options["processes"] = list(chain.from_iterable(ALL_PROCESSES))
        options["process"] = RANK

        self.__set_logger_parallel(MACHINE_NUMBER_STRING,
                                   MACHINE_RANK_NAME,
                                   options)

        MPI.COMM_WORLD.barrier()
        logging.debug("Rank : %i - Size : %i - host : %s", RANK, SIZE,
                      socket.gethostname())
        IP = socket.gethostbyname(socket.gethostname())
        logging.debug("ip address is : %s", IP)
        self.call_mpi__barrier()
        logging.debug("LD_LIBRARY_PATH is %s",  os.getenv('LD_LIBRARY_PATH'))
        self.call_mpi__barrier()

    def call_mpi__barrier(self):
        """ Call MPI _barrier before an experiment is created.
        """
        logging.debug("Waiting at the _barrier")
        MPI.COMM_WORLD.barrier()

    def __get_log_level(self, options):
        """ Gets the right log level for the flags -v or -q
        """
        if ('verbose' in options) and options['verbose']:
            return logging.DEBUG
        if ('quiet' in options) and options['quiet']:
            return logging.WARN
        return logging.INFO

    def __set_logger_single(self, options):
        """ Set single-threaded logging.
        """
        logger = logging.getLogger()
        logger.setLevel(self.__get_log_level(options))

        fh = logging.FileHandler(os.path.join(options["log_path"],
                                              'log.txt'), mode='w')
        fh.setFormatter(logging.Formatter('L %(relativeCreated)12d M CPU0 0' +
                                          ' %(levelname)-6s %(message)s'))
        logger.addHandler(fh)

        cu.add_user_log_level()
        cu.add_user_log_handler(logger, os.path.join(options["log_path"],
                                                     'user.log'))
        if 'syslog_server' in options.keys():
            try:
                cu.add_syslog_log_handler(logger, options['syslog_server'],
                                          options['syslog_port'])
            except:
                msg = "Unable to add syslog logging for server %s on port %i"
                logger.warn(msg, options['syslog_server'],
                            options['syslog_port'])

    def __set_logger_parallel(self, number, rank, options):
        """ Set parallel logger.
        """
        logging.basicConfig(level=self.__get_log_level(options),
                            format='L %(relativeCreated)12d M' +
                            number + ' ' + rank +
                            ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

        # Only add user logging to the 0 rank process so we don't get
        # a lot of output, just a summary, but we want the user messages
        # tagged in all rank processes
        cu.add_user_log_level()
        if MPI.COMM_WORLD.rank == 0:
            logger = logging.getLogger()
            cu.add_user_log_handler(logger,
                                    os.path.join(options["out_path"],
                                                 'user.log'))
            if 'syslog_server' in options.keys():
                try:
                    cu.add_syslog_log_handler(logger,
                                              options['syslog_server'],
                                              options['syslog_port'])
                except:
                    logger.warn("Unable to add syslog logging for server %s on port %i",
                                options['syslog_server'],
                                options['syslog_port'])
