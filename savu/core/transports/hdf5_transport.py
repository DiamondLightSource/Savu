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
.. module:: hdf5_transport
   :platform: Unix
   :synopsis: Transport specific plugin list runner, passes the data to and \
       from the plugin.

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging
import socket
import os
import copy
import numpy as np

from mpi4py import MPI
from itertools import chain
from savu.core.transport_control import TransportControl
import savu.plugins.utils as pu
import savu.core.utils as cu


class Hdf5Transport(TransportControl):

    def _transport_control_setup(self, options):
        """ Fill the options dictionary with MPI related values.
        """
        processes = options["process_names"].split(',')

        if len(processes) is 1:
            options["mpi"] = False
            self.mpi = False
            options["process"] = 0
            options["processes"] = processes
            self.__set_logger_single(options)
        else:
            options["mpi"] = True
            self.mpi = True
            print("Options for mpi are")
            print(options)
            self.__mpi_setup(options)

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
        index = sorted(range(len(rank_map)), key=lambda k: rank_map[k])
        all_processes = [(names*n_nodes)[index[i]] for i in range(n_cores)]
        options['processes'] = all_processes
        rank = MPI.COMM_WORLD.rank
        options['process'] = rank
        node_number = rank_map.index(rank)/n_cores_per_node
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
        log_format = 'L %(relativeCreated)12d M CPU0 0' + \
                     ' %(levelname)-6s %(message)s'
        self.__set_logger(log_format, options, tofile=True)
        cu.add_user_log_level()
        self.__add_user_logging(options)
        self.__add_console_logging()

    def __set_logger_parallel(self, number, rank, options):
        """ Set parallel logger.
        """
        log_format = 'L %(relativeCreated)12d M' + number + ' ' + rank +\
                     ' %(levelname)-6s %(message)s'
        if options['cluster']:
            self.__set_logger(log_format, options)
        else:
            self.__set_logger(log_format, options, tofile=True)

        # Only add user logging to the 0 rank process only
        cu.add_user_log_level()
        if MPI.COMM_WORLD.rank == 0:
            self.__add_user_logging(options)
            if not options['cluster']:
                self.__add_console_logging()

    def __set_logger(self, fmat, options, tofile=False):
        level = self.__get_log_level('options')
        datefmt = '%H:%M:%S'
        if tofile:
            filename = os.path.join(options['log_path'], 'log.txt')
            logging.basicConfig(level=level, format=fmat, datefmt=datefmt,
                                filename=filename, filemode='w')
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
        filename = os.path.join(options['out_path'], 'user_log')
        cu.add_user_log_handler(logger, filename)
        if 'syslog_server' in options.keys():
            try:
                cu.add_syslog_log_handler(logger, options['syslog_server'],
                                          options['syslog_port'])
            except:
                logger.warn("Unable to add syslog logging for server %s on"
                            " port %i", options['syslog_server'],
                            options['syslog_port'])

    def _transport_run_plugin_list(self):
        """ Run the plugin list inside the transport layer.
        """
        exp = self.exp

        plugin_obj = exp.meta_data.plugin_list
        n_loaders = plugin_obj._get_n_loaders()
        plugin_list = exp.meta_data.plugin_list.plugin_list

        for i in range(n_loaders):
            pu.plugin_loader(exp, plugin_list[i])

        start = n_loaders
        stop = 0
        n_plugins = len(plugin_list) - 1  # minus 1 for saver

        while n_plugins != stop:
            start_in_data = copy.deepcopy(self.exp.index['in_data'])
            in_data = exp.index["in_data"][exp.index["in_data"].keys()[0]]

            out_data_objs, stop = in_data._load_data(start)
            exp._clear_data_objects()

            self.exp.index['in_data'] = copy.deepcopy(start_in_data)
            self.__real_plugin_run(plugin_list, out_data_objs, start, stop)
            start = stop

        self.exp._barrier()
        self.exp._clean_up_files()

        return

    def __real_plugin_run(self, plugin_list, out_data_objs, start, stop):
        """ Execute the plugin.
        """
        exp = self.exp
        for i in range(start, stop):
            link_type = "final_result" if i is len(plugin_list)-2 else \
                "intermediate"

            exp._barrier()
            for key in out_data_objs[i - start]:
                exp.index["out_data"][key] = out_data_objs[i - start][key]

            exp._barrier()
            plugin = pu.plugin_loader(exp, plugin_list[i])

            exp._barrier()
            cu.user_message("*Running the %s plugin*" % (plugin_list[i]['id']))
            plugin._run_plugin(exp, self)

            exp._barrier()
            if self.mpi:
                cu.user_messages_from_all(plugin.name,
                                          plugin.executive_summary())
            else:
                for message in plugin.executive_summary():
                    cu.user_message("%s - %s" % (plugin.name, message))

            out_datasets = plugin.parameters["out_datasets"]
            plugin._clean_up()
            exp._reorganise_datasets(out_datasets, link_type)

    def _process(self, plugin):
        """ Organise required data and execute the main plugin processing.

        :param plugin plugin: The current plugin instance.
        """
        in_data, out_data = plugin.get_datasets()

        expInfo = plugin.exp.meta_data
        in_slice_list, in_global_frame_idx = \
            self.__get_all_slice_lists(in_data, expInfo)
        out_slice_list, _ = self.__get_all_slice_lists(out_data, expInfo)
        plugin.set_global_frame_index(in_global_frame_idx)

        squeeze_dict = self.__set_functions(in_data, 'squeeze')
        expand_dict = self.__set_functions(out_data, 'expand')

        number_of_slices_to_process = len(in_slice_list[0])
        for count in range(number_of_slices_to_process):
            percent_complete = count/(number_of_slices_to_process * 0.01)
            cu.user_message("%s - %3i%% complete" %
                            (plugin.name, percent_complete))

            section, slice_list = \
                self.__get_all_padded_data(in_data, in_slice_list, count,
                                           squeeze_dict)
            plugin.set_current_slice_list(slice_list)
            result = plugin.process_frames(section)
            self.__set_out_data(out_data, out_slice_list, result, count,
                                expand_dict)

        cu.user_message("%s - 100%% complete" % (plugin.name))
        plugin._revert_preview(in_data)

    def __set_functions(self, data_list, name):
        """ Create a dictionary of functions to remove (squeeze) or re-add
        (expand) dimensions, of length 1, from each dataset in a list.

        :param list(Data) data_list: Datasets
        :param str name: 'squeeze' or 'expand'
        :returns: A dictionary of lambda functions
        :rtype: dict
        """
        str_name = 'self.' + name + '_output'
        function = {'expand': self.__create_expand_function,
                    'squeeze': self.__create_squeeze_function}
        ddict = {}
        for i in range(len(data_list)):
            ddict[i] = {i: str_name + str(i)}
            ddict[i] = function[name](data_list[i])
        return ddict

    def __create_expand_function(self, data):
        """ Create a function that re-adds missing dimensions of length 1.

        :param Data data: Dataset
        :returns: expansion function
        :rtype: lambda
        """
        slice_dirs = data._get_plugin_data().get_slice_directions()
        n_core_dirs = len(data._get_plugin_data().get_core_directions())
        new_slice = [slice(None)]*len(data.get_shape())
        possible_slices = [copy.copy(new_slice)]

        if len(slice_dirs) > 1:
            for sl in slice_dirs[1:]:
                new_slice[sl] = None
        possible_slices.append(copy.copy(new_slice))
        new_slice[slice_dirs[0]] = None
        possible_slices.append(copy.copy(new_slice))
        possible_slices = possible_slices[::-1]
        return lambda x: x[possible_slices[len(x.shape)-n_core_dirs]]

    def __create_squeeze_function(self, data):
        """ Create a function that removes dimensions of length 1.

        :param Data data: Dataset
        :returns: squeeze function
        :rtype: lambda
        """
        max_frames = data._get_plugin_data()._get_frame_chunk()
        squeeze_dims = data._get_plugin_data().get_slice_directions()
        if max_frames > 1:
            squeeze_dims = squeeze_dims[1:]
        return lambda x: np.squeeze(x, axis=squeeze_dims)

    def __get_all_slice_lists(self, data_list, expInfo):
        """ Get all slice lists for the current process.

        :param list(Data) data_list: Datasets
        :param: meta_data expInfo: The experiment metadata.
        :returns: slice lists.
        :rtype: list(tuple(slice))
        """
        slice_list = []
        global_frame_index = []
        for data in data_list:
            sl, f = data._get_slice_list_per_process(expInfo)
            slice_list.append(sl)
            global_frame_index.append(f)
        return slice_list, global_frame_index

    def __get_all_padded_data(self, data_list, slice_list, count,
                              squeeze_dict):
        """ Get all padded slice lists.

        :param Data data_list: datasets
        :param list(list(slice)) slice_list: slice lists for datasets
        :param int count: frame number.
        :param dict squeeze_dict: squeeze functions for datasets
        :returns: all data for this frame and associated padded slice lists
        :rtype: list(np.ndarray), list(tuple(slice))
        """
        section = []
        slist = []
        for idx in range(len(data_list)):
            section.append(squeeze_dict[idx](
                data_list[idx]._get_padded_slice_data(slice_list[idx][count])))
            slist.append(slice_list[idx][count])
        return section, slist

    def __set_out_data(self, data_list, slice_list, result, count,
                       expand_dict):
        """ Transfer plugin results for current frame to backing files.

        :param list(Data) data_list: datasets
        :param list(list(slice)) slice_list: slice lists for datasets
        :param list(np.ndarray) result: plugin results
        :param int count: frame number
        :param dict expand_dict: expand functions for datasets
        """
        result = [result] if type(result) is not list else result
        for idx in range(len(data_list)):
            data_list[idx].data[slice_list[idx][count]] = \
                data_list[idx]._get_unpadded_slice_data(
                    slice_list[idx][count], expand_dict[idx](result[idx]))
