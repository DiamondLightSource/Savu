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
   :synopsis: Transport specific plugin list runner, passes the data to and
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
        self.call_mpi_barrier()
        logging.debug("LD_LIBRARY_PATH is %s",  os.getenv('LD_LIBRARY_PATH'))
        self.call_mpi_barrier()

    def call_mpi_barrier(self):
        """ Call MPI barrier before an experiment is created.
        """
        logging.debug("Waiting at the barrier")
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

        fh = logging.FileHandler(os.path.join(options["out_path"], 'log.txt'),
                                 mode='w')
        fh.setFormatter(logging.Formatter('L %(relativeCreated)12d M CPU0 0' +
                                          ' %(levelname)-6s %(message)s'))
        logger.addHandler(fh)

        cu.add_user_log_level()
        cu.add_user_log_handler(logger, os.path.join(options["out_path"],
                                                     'user.log'))

    def __set_logger_parallel(self, number, rank, options):
        """ Set parallel logger.
        """
        logging.basicConfig(level=self.get_log_level(options),
                            format='L %(relativeCreated)12d M' +
                            number + ' ' + rank +
                            ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

        # Only add user logging to the 0 rank process so we don't get
        # a lot of output, just a summary, but we want the user messages
        # tagged in all rank processes
        cu.add_user_log_level()
        if MPI.COMM_WORLD.rank == 0:
            logging.getLogger()
            cu.add_user_log_handler(logging.getLogger(),
                                    os.path.join(options["out_path"],
                                                 'user.log'))

    def _transport_run_plugin_list(self):
        """ Run the plugin list inside the transport layer.
        """
        exp = self.exp

        plugin_list = exp.meta_data.plugin_list.plugin_list
        pu.plugin_loader(exp, plugin_list[0])

        start = 1
        stop = start
        n_plugins = len(plugin_list[start:-1]) + 1
        while n_plugins != stop:
            start_in_data = copy.deepcopy(self.exp.index['in_data'])
            in_data = exp.index["in_data"][exp.index["in_data"].keys()[0]]

            out_data_objs, stop = in_data.load_data(start)
            exp.clear_data_objects()

            self.exp.index['in_data'] = copy.deepcopy(start_in_data)
            self.__real_plugin_run(plugin_list, out_data_objs, start, stop)
            start = stop

        for key in exp.index["in_data"].keys():
            exp.index["in_data"][key].close_file()

        return

    def __real_plugin_run(self, plugin_list, out_data_objs, start, stop):
        """ Execute the plugin.
        """
        exp = self.exp
        for i in range(start, stop):
            link_type = "final_result" if i is len(plugin_list)-2 else \
                "intermediate"

            exp.barrier()

            for key in out_data_objs[i - start]:
                exp.index["out_data"][key] = out_data_objs[i - start][key]

            exp.barrier()
            plugin = pu.plugin_loader(exp, plugin_list[i])

            exp.barrier()
            cu.user_message("*Running the %s plugin*" % (plugin_list[i]['id']))
            plugin.run_plugin(exp, self)

            exp.barrier()
            if self.mpi:
                cu.user_messages_from_all(plugin.name,
                                          plugin.executive_summary())
            else:
                for message in plugin.executive_summary():
                    cu.user_message("%s - %s" % (plugin.name, message))

            exp.barrier()
            out_datasets = plugin.parameters["out_datasets"]
            exp.reorganise_datasets(out_datasets, link_type)

    def _process(self, plugin):
        """ Organise required data and execute the main plugin processing.

        :param plugin plugin: The current plugin instance.
        """
        self.process_checks()
        in_data, out_data = plugin.get_datasets()

        for data in out_data:
            print data.get_shape()
        expInfo = plugin.exp.meta_data
        in_slice_list = self.__get_all_slice_lists(in_data, expInfo)
        out_slice_list = self.__get_all_slice_lists(out_data, expInfo)

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
            result = plugin.process_frames(section, slice_list)
            self.__set_out_data(out_data, out_slice_list, result, count,
                                expand_dict)

        cu.user_message("%s - 100%% complete" % (plugin.name))
        plugin._revert_preview(in_data)

    def process_checks(self):
        pass
        # if plugin inherits from base_recon and the data inherits from tomoraw
        # then throw an exception
#        if isinstance(in_data, TomoRaw):
#            raise Exception("The input data to a reconstruction plugin cannot
#            be Raw data. Have you performed a timeseries_field_correction?")
# call a new process called process_check?

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
        max_frames = data._get_plugin_data().get_frame_chunk()
        if data.mapping:
            map_obj = self.exp.index['mapping'][data.get_name()]
            map_dim_len = map_obj.data_info.get_meta_data('map_dim_len')
            max_frames = min(max_frames, map_dim_len)
            data._get_plugin_data().set_frame_chunk(max_frames)

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
        for data in data_list:
            slice_list.append(data.get_slice_list_per_process(expInfo))
        return slice_list

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
                data_list[idx].get_padded_slice_data(slice_list[idx][count])))
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
            temp = data_list[idx].get_unpadded_slice_data(
                slice_list[idx][count], result[idx])
            data_list[idx].data[slice_list[idx][count]] = \
                expand_dict[idx](temp)

#    def _transfer_to_meta_data(self, return_dict):
#        """
#        """
#        remove_data_sets = []
#        for data_key in return_dict.keys():
#            for name in return_dict[data_key].keys():
#                convert_data = return_dict[data_key][name]
#                remove_data_sets.append(convert_data.name)
#                data_key.meta_data.set_meta_data(name, convert_data.data[...])
#        return remove_data_sets
