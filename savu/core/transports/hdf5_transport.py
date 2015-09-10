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
import numpy as np
import socket
import os
import copy

from mpi4py import MPI
from itertools import chain
from savu.core.utils import logfunction
from savu.data.transport_mechanism import TransportMechanism
from savu.core.utils import logmethod


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
        logging.debug("Rank : %i - Size : %i - host : %s", RANK, SIZE, socket.gethostname())   
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
        fh = logging.FileHandler(os.path.join(options["out_path"],'log.txt'), mode='w')
        fh.setFormatter(logging.Formatter('L %(relativeCreated)12d M CPU0 0' +
                                          ' %(levelname)-6s %(message)s'))
        logger.addHandler(fh)
        logging.info("Starting the reconstruction pipeline process")
    
       
    def set_logger_parallel(self, number, rank):
        logging.basicConfig(level=0, format='L %(relativeCreated)12d M' +
                            number + ' ' + rank +
                            ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')
        logging.info("Starting the reconstruction pipeline process")
    

    def transport_run_plugin_list(self, exp):
        """Runs a chain of plugins
        """        
        plugin_list = exp.meta_data.plugin_list.plugin_list
        # run the loader plugin
        self.plugin_loader(exp, plugin_list[0])
        # create all output data_objects and backing files        
        in_data = exp.index["in_data"][exp.index["in_data"].keys()[0]]
        out_data_objects = in_data.load_data(self, exp)

        # clear all out_data objects in experiment dictionary
        exp.clear_data_objects()
        
        print "running the plugins"
        self.plugin_loader(exp, plugin_list[0])
        
        for i in range(1, len(plugin_list)-1):
            print plugin_list[i]["id"]
            
            for key in out_data_objects[i-1]:
                exp.index["out_data"][key] = out_data_objects[i-1][key]

            plugin = self.plugin_loader(exp, plugin_list[i], pos=i)
            plugin.run_plugin(exp, self)


            if exp.meta_data.get_meta_data('mpi') is True: # do i need this block?
                MPI.COMM_WORLD.Barrier()
                logging.debug("Blocking till all processes complete")
        
            # delete fixed directions, as this is related only to the finished 
            # plugin and not to the dataset 
            for in_objs in plugin.parameters["in_datasets"]:
                exp.index["in_data"][in_objs].delete_fixed_directions()
        
            # close any files that are no longer required
            for out_objs in plugin.parameters["out_datasets"]:
                if out_objs in exp.index["in_data"].keys():
                    exp.index["in_data"][out_objs].save_data()
            
            for key in exp.index["out_data"]:
                exp.index["in_data"][key] = \
                               copy.deepcopy(exp.index["out_data"][key])                               

##            if plugin == 0:
##                cite_info = plugin.get_citation_information()
##                if cite_info is not None:
##                    plugin_list.add_plugin_citation(output_filename, count,
##                                                      cite_info)
##                group_name = "%i-%s" % (count, plugin.name)
##                plugin_list.add_intermediate_data_link(output_filename,
##                                                        output, group_name)
            exp.clear_out_data_objects()

        # close all remaining files
        for key in exp.index["in_data"].keys():
            exp.index["in_data"][key].save_data()

        return 

    @logmethod
    def timeseries_field_correction(self, plugin, in_data, out_data, expInfo, params):

        in_data = in_data[0]
        out_data = out_data[0]

        dark = in_data.meta_data.get_meta_data("dark")
        flat = in_data.meta_data.get_meta_data("flat")

        [in_slice_list, frame_list] = in_data.get_slice_list_per_process(expInfo)
        [out_slice_list, frame_list] = out_data.get_slice_list_per_process(expInfo)

        for count in range(len(in_slice_list)):
            idx = frame_list[count]
            out_data.data[out_slice_list[count]] = \
                      plugin.correction(in_data.data[in_slice_list[count]], 
                                        dark[idx, :], flat[idx, :], params)

        in_slice_list = in_data.get_grouped_slice_list()


    @logmethod
    def reconstruction_setup(self, plugin, in_data, out_data, expInfo, params):

        in_data = in_data[0]
        out_data = out_data[0]

        [slice_list, frame_list] = in_data.get_slice_list_per_process(expInfo)
        cor = in_data.meta_data.get_meta_data("centre_of_rotation")[frame_list]

        count = 0
        for sl in slice_list:
            frame = plugin.reconstruct(np.squeeze(in_data.data[sl]),
                                       cor[count],
                                       out_data.get_pattern_shape(),
                                       params)
            out_data.data[sl] = frame
            count += 1
            plugin.count += 1
            print plugin.count

    def filter_chunk(self, plugin, in_data, out_data, expInfo, params):
        logging.debug("Running filter._filter_chunk")

        in_slice_list = []
        for ind in range(len(in_data)):
            [slice_list, frame_list] = in_data[ind].get_slice_list_per_process(expInfo)
            in_slice_list.append(slice_list)

        out_data = out_data[0]
        [out_slice_list, frame_list] = out_data.get_slice_list_per_process(expInfo)

        padding = plugin.get_filter_padding()

        for count in range(len(in_slice_list[0])):
            section = []
            for ind in range(len(in_data)):
                section.append(in_data[ind].get_padded_slice_data(
                            in_slice_list[ind][count], padding, in_data[ind]))
            result = plugin.filter_frame(section, params)

            if type(result) == dict:
                for key in result.keys():
                    if key == 'center_of_rotation':
                        frame = in_data[0].get_orthogonal_slice(in_slice_list[count], 
                        in_data[0].core_directions[plugin.get_filter_frame_type()])
                        out_data.center_of_rotation[frame] = result[key]
                    elif key == 'data':
                        out_data.data[out_slice_list[count]] = \
                        in_data[0].get_unpadded_slice_data(in_slice_list[count], 
                                                    padding, in_data[0], result)
            else:
                out_data.data[out_slice_list[count]] = \
                in_data[0].get_unpadded_slice_data(in_slice_list[0][count], padding, 
                                                in_data[0], result)
