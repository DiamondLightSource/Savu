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
            self.mpi_setup(options)

        
    def mpi_setup(self, options):
        
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
        #*** check base saver is to hdf5 file?
        in_data = exp.index["in_data"][exp.index["in_data"].keys()[0]]
        out_data_objects = in_data.load_data(self, exp)

        # clear all out_data objects in experiment dictionary
        exp.index["out_data"] = {}        
        
        count = 0
        for plugin_dict in exp.info["plugin_list"][1:-1]:
            
            
            logging.debug("Loading plugin %s", plugin_dict['id'])
            plugin_id = plugin_dict["id"]

            plugin = self.load_plugin(plugin_id)

            plugin.setup(exp)

            for key in out_data_objects[count]:
                exp.index["out_data"][key] = out_data_objects[count][key]
      
            plugin.set_parameters(plugin_dict['data'])

            logging.debug("Starting processing  plugin %s", plugin_id)
            plugin.run_plugin(exp, self)
            logging.debug("Completed processing plugin %s", plugin_id)


            for out_objs in exp.info["plugin_objects"]["out_data"]:
                if out_objs in exp.index["in_data"].keys():
                    exp.index["in_data"][out_objs].save_data()

            for key in exp.index["out_data"]:
                exp.index["in_data"][key] = \
                               copy.deepcopy(exp.index["out_data"][key])

            if exp.info['mpi'] is True: # do i need this block?
                MPI.COMM_WORLD.Barrier()
                logging.debug("Blocking till all processes complete")
                
            count += 1    
 
#            if plugin == 0:
#                cite_info = plugin.get_citation_information()
#                if cite_info is not None:
#                    plugin_list.add_plugin_citation(output_filename, count,
#                                                      cite_info)
#                group_name = "%i-%s" % (count, plugin.name)
#                plugin_list.add_intermediate_data_link(output_filename,
#                                                        output, group_name)
#
        for key in exp.index["in_data"].keys():
            exp.index["in_data"][key].save_data()
    
    
    @logmethod
    def timeseries_field_correction(self, plugin, in_data, out_data, info, params):
   
        dark = in_data.info["dark"]
        flat = in_data.info["flat"]   
   
        # get a list of all the frames
        output_frames = np.arange(in_data.get_shape()[1])
        frames = np.array_split(output_frames, 
                                len(info["processes"]))[info["process"]]                            

        for i in frames: 
            out_data.data[out_data.get_index([i])] = plugin.correction(
            in_data.get_frame_raw([i]), dark[i,:], flat[i,:], params)
            
            
    @logmethod
    def reconstruction_setup(self, plugin, in_data, out_data, info, params):

        processes = info["processes"]
        process = info["process"]
        
        centre_of_rotations = np.array_split(info["centre_of_rotation"], len(processes))[process]
        sinogram_frames = np.arange(in_data.get_nPattern())    
        frames = np.array_split(sinogram_frames, len(processes))[process]
            
        count = 0
        for i in frames:
            out_data.data[out_data.get_index([i])] = \
                plugin.reconstruct(in_data.get_frame([i]),
                                   centre_of_rotations[count],
                                   out_data.get_pattern_shape(), 
                                   params)
            count += 1
            plugin.count+=1
            print plugin.count
    

    @logmethod
    def filter_set_up(self, params):    
        param_name = []
        for name in param_name: 
            for p in params:
                globals()[name] = p
        pass
    
