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
.. module:: HDF5
   :platform: Unix
   :synopsis: Transport for saving and loading files using hdf5

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging
import socket
import os
import copy
import numpy as np

from mpi4py import MPI
from itertools import chain
from savu.core.utils import logfunction
from savu.data.transport_mechanism import TransportMechanism
from savu.core.utils import logmethod
import savu.plugins.utils as pu


class Hdf5Transport(TransportMechanism):

    def transport_control_setup(self, options):
        processes = options["process_names"].split(',')

        if len(processes) is 1:
            options["mpi"] = False
            options["process"] = 0
            options["processes"] = processes
            self.set_logger_single(options)
        else:
            options["mpi"] = True
            print("Options for mpi are")
            print(options)
            self.mpi_setup(options)

    def mpi_setup(self, options):
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

        self.set_logger_parallel(MACHINE_NUMBER_STRING, MACHINE_RANK_NAME)

        MPI.COMM_WORLD.barrier()
        logging.info("Starting the reconstruction pipeline process")
        logging.debug("Rank : %i - Size : %i - host : %s", RANK, SIZE,
                      socket.gethostname())
        IP = socket.gethostbyname(socket.gethostname())
        logging.debug("ip address is : %s", IP)
        self.call_mpi_barrier()
        logging.debug("LD_LIBRARY_PATH is %s",  os.getenv('LD_LIBRARY_PATH'))
        self.call_mpi_barrier()

    @logfunction
    def call_mpi_barrier(self):
        logging.debug("Waiting at the barrier")
        MPI.COMM_WORLD.barrier()

    def set_logger_single(self, options):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(os.path.join(options["out_path"], 'log.txt'),
                                 mode='w')
        fh.setFormatter(logging.Formatter('L %(relativeCreated)12d M CPU0 0' +
                                          ' %(levelname)-6s %(message)s'))
        logger.addHandler(fh)
        logging.info("Starting the reconstruction pipeline process")

    def set_logger_parallel(self, number, rank):
        logging.basicConfig(level=0, format='L %(relativeCreated)12d M' +
                            number + ' ' + rank +
                            ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')
        logging.info("Starting the reconstruction pipeline process")

    def transport_run_plugin_list(self):
        """
        Runs a chain of plugins
        """
        exp = self.exp
        exp.barrier()
        logging.info("Starting the HDF5 plugin list runner")
        plugin_list = exp.meta_data.plugin_list.plugin_list

        exp.barrier()
        logging.info("run the loader plugin")
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
            self.real_plugin_run(plugin_list, out_data_objs, start, stop)
            start = stop

        exp.barrier()
        logging.info("close all remaining files")
        for key in exp.index["in_data"].keys():
            exp.index["in_data"][key].close_file()

        exp.barrier()
        logging.info("Completing the HDF5 plugin list runner")
        return

    def real_plugin_run(self, plugin_list, out_data_objs, start, stop):
        exp = self.exp
        for i in range(start, stop):
            link_type = "final_result" if i is len(plugin_list)-2 else \
                "intermediate"

            logging.info("Running Plugin %s" % plugin_list[i]["id"])
            exp.barrier()

            logging.info("Initialise output data")
            for key in out_data_objs[i - start]:
                exp.index["out_data"][key] = out_data_objs[i - start][key]

            exp.barrier()
            logging.info("Load the plugin")
            plugin = pu.plugin_loader(exp, plugin_list[i])

            exp.barrier()
            logging.info("run the plugin")
            print "\n*running the", plugin_list[i]['id'], "plugin*\n"
            plugin.run_plugin(exp, self)

            exp.barrier()
            logging.info("close any files that are no longer required")
            out_datasets = plugin.parameters["out_datasets"]

            exp.reorganise_datasets(out_datasets, link_type)

    def process(self, plugin):
        self.process_checks()
        in_data, out_data = plugin.get_datasets()
        expInfo = plugin.exp.meta_data
        in_slice_list = self.get_all_slice_lists(in_data, expInfo)
        out_slice_list = self.get_all_slice_lists(out_data, expInfo)
        squeeze_dict = self.set_functions(in_data, 'squeeze')
        expand_dict = self.set_functions(out_data, 'expand')

        for count in range(len(in_slice_list[0])):
            # print every 10th loop iteration to screen
            if (count % 10) == 0:
                print count

            section, slice_list = \
                self.get_all_padded_data(in_data, in_slice_list, count,
                                         squeeze_dict)
            result = plugin.process_frames(section, slice_list)
            self.set_out_data(out_data, out_slice_list, result, count,
                              expand_dict)

    def process_checks(self):
        pass
        # if plugin inherits from base_recon and the data inherits from tomoraw
        # then throw an exception
#        if isinstance(in_data, TomoRaw):
#            raise Exception("The input data to a reconstruction plugin cannot
#            be Raw data. Have you performed a timeseries_field_correction?")
# call a new process called process_check?

    def set_functions(self, data_list, name):
        str_name = 'self.' + name + '_output'
        function = {'expand': self.create_expand_function,
                    'squeeze': self.create_squeeze_function}
        ddict = {}
        for i in range(len(data_list)):
            ddict[i] = {i: str_name + str(i)}
            ddict[i] = function[name](data_list[i])
        return ddict

    def create_expand_function(self, data):
        slice_dirs = data.get_plugin_data().get_slice_directions()
        n_core_dirs = len(data.get_plugin_data().get_core_directions())
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

    def create_squeeze_function(self, data):
        max_frames = data.get_plugin_data().get_frame_chunk()
        if data.mapping:
            map_obj = self.exp.index['mapping'][data.get_name()]
            map_dim_len = map_obj.data_info.get_meta_data('map_dim_len')
            max_frames = min(max_frames, map_dim_len)
            data.get_plugin_data().set_frame_chunk(max_frames)

        squeeze_dims = data.get_plugin_data().get_slice_directions()
        if max_frames > 1:
            squeeze_dims = squeeze_dims[1:]
        if data.variable_length_flag:
            unravel = lambda x, i: unravel(x[0], i-1) if i > 0 else x
            return lambda x: np.squeeze(unravel(x, len(data.get_shape())-1),
                                        axis=squeeze_dims)
        return lambda x: np.squeeze(x, axis=squeeze_dims)

    def get_all_slice_lists(self, data_list, expInfo):
        slice_list = []
        for data in data_list:
            slice_list.append(data.get_slice_list_per_process(expInfo))
        return slice_list

    def get_all_padded_data(self, data, slice_list, count, squeeze_dict):
        section = []
        slist = []
        for idx in range(len(data)):
            section.append(squeeze_dict[idx](
                data[idx].get_padded_slice_data(slice_list[idx][count])))
            slist.append(slice_list[idx][count])
        return section, slist

    def set_out_data(self, data, slice_list, result, count, expand_dict):
        result = [result] if type(result) is not list else result
        for idx in range(len(data)):
            temp = data[idx].get_unpadded_slice_data(slice_list[idx][count],
                                                     result[idx])
            data[idx].data[slice_list[idx][count]] = expand_dict[idx](temp)

    def transfer_to_meta_data(self, return_dict):
        remove_data_sets = []
        for data_key in return_dict.keys():
            for name in return_dict[data_key].keys():
                convert_data = return_dict[data_key][name]
                remove_data_sets.append(convert_data.name)
                data_key.meta_data.set_meta_data(name, convert_data.data[...])
        return remove_data_sets
