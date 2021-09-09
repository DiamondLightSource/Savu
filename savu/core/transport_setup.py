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
import savu.core.utils as cu


class MPI_setup(object):

    def __init__(self, options, name='MPI_setup'):
        self.__set_dictionary(options)

    def __set_dictionary(self, options):
        """ Fill the options dictionary with MPI related values.
        """
        processes = options["process_names"].split(',')

        if len(processes) == 1:
            options["mpi"] = False
            options["process"] = 0
            options["processes"] = processes
            self.__set_logger_single(options)
        else:
            options["mpi"] = True
            self.__mpi_setup(options)

        logging.debug(options)

    def __mpi_setup(self, options):
        """ Set MPI process specific values and logging initialisation.
        """
        hosts = MPI.COMM_WORLD.allgather(socket.gethostname())
        uniq_hosts = set(hosts)
        names = options['process_names'].split(',')

        n_cores = len(hosts)
        n_nodes = len(uniq_hosts)
        n_cores_per_node = len(names)

        rank_map = [i for s in uniq_hosts for i in range(n_cores)
                    if s == hosts[i]]
        index = sorted(list(range(len(rank_map))), key=lambda k: rank_map[k])
        all_processes = [(names*n_nodes)[index[i]] for i in range(n_cores)]
        options['processes'] = all_processes
        rank = MPI.COMM_WORLD.rank
        options['process'] = rank
        node_number = rank_map.index(rank) // n_cores_per_node
        local_name = all_processes[rank]

        self.__set_logger_parallel("%03i" % node_number, local_name, options)

        MPI.COMM_WORLD.barrier()
        logging.debug("Rank : %i - Size : %i - host : %s", rank, n_cores,
                      hosts[MPI.COMM_WORLD.rank])

        IP = socket.gethostbyname(socket.gethostname())
        logging.debug("ip address is : %s", IP)
        self.call_mpi__barrier()
        logging.debug("LD_LIBRARY_PATH is %s",  os.getenv('LD_LIBRARY_PATH'))
        self.call_mpi__barrier()

    def call_mpi__barrier(self):
        """ Call MPI_barrier before an experiment is created.
        """
        logging.debug("Waiting at the _barrier")
        MPI.COMM_WORLD.barrier()

    def __set_logger_single(self, options):
        """ Set single-threaded logging.
        """
        log_format = 'L %(relativeCreated)12d M000 CPU00' + \
                     ' %(levelname)-6s %(message)s'
        log_dir = self.__get_log_directory(options)
        filename = os.path.join(log_dir, 'log.txt')
        level = cu._get_log_level(options)
        self.__set_logger(level, log_format, fname=filename)
        cu.add_user_log_level()
        self.__add_user_logging(options)
        self.__add_console_logging()

    def __set_logger_parallel(self, number, rank, options):
        """ Set parallel logger.
        """
        machine = 'M%-5s%-6s' % (number, rank)
        log_format = 'L %(relativeCreated)12d ' + machine +\
                     ' %(levelname)-6s %(message)s'
        level = cu._get_log_level(options)
        self.__set_logger(level, log_format)

        # Only add user logging to the 0 rank process
        cu.add_user_log_level()
        if MPI.COMM_WORLD.rank == 0:
            self.__add_user_logging(options)
            if not options['cluster']:
                self.__add_console_logging()

    def __set_logger(self, level, fmat, fname=None):
        datefmt = '%H:%M:%S'
        if fname:
            logging.basicConfig(level=level, format=fmat, datefmt=datefmt,
                                filename=fname, filemode='w')
        else:
            logging.basicConfig(level=level, format=fmat, datefmt=datefmt)

    def __add_console_logging(self):
        console = logging.StreamHandler()
        console.setLevel(cu.USER_LOG_LEVEL)
#        formatter = \
#            logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        formatter = \
            logging.Formatter('%(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def __add_user_logging(self, options):
        logger = logging.getLogger()
        log_dir = self.__get_log_directory(options)
        filename = os.path.join(log_dir, "user.log")
        cu.add_user_log_handler(logger, filename)
        if 'syslog_server' in list(options.keys()):
            try:
                cu.add_syslog_log_handler(logger, options['syslog_server'],
                                          options['syslog_port'])
            except:
                logger.warn("Unable to add syslog logging for server %s on"
                            " port %i", options['syslog_server'],
                            options['syslog_port'])

    def __get_log_directory(self, options):
        """Create run_log directory to hold log files

        :param options: dictionary holding the directory
          to hold result files
        :return: str, directory for log files
        """
        log_dir = os.path.join(options['out_path'],"run_log")
        if not os.path.exists(log_dir):
            os.makedirs(os.path.join(log_dir))
        return log_dir
