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

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os
import logging
import sys

import h5py        

from savu.data.TransportMechanism import TransportMechanism
from savu.core.utils import logfunction
import savu.plugins.utils as pu
from savu.data.structures import RawTimeseriesData, ProjectionData, VolumeData

from contextlib import closing
from distarray.globalapi import Context, Distribution
from distarray.globalapi.distarray import DistArray as da


import savu.data.transports.dist_array_utils as du

class DistArrayTransport(TransportMechanism):

    def __init__(self, plugin_list, args):
        self.run_plugin_list(args[0], plugin_list, args[2]) 
        
        
    @logfunction
    def run_plugin_list(self, input_file, plugin_list, processing_dir, 
                        processes=["CPU0"], process=0):
        """Runs a chain of plugins
    
        :param input_file: The input file name.
        :type input_file: str.
        :param plugin_list: Plugin list.
        :type plugin_list: savu.data.structure.PluginList.
        :param processing_dir: Location of the processing directory.
        :type processing_dir: str.
        :param mpi: Whether this is running in mpi, default is false.
        :type mpi: bool.
        """
        
        logging.debug("processing Plugins")
        
        targets = [0, 1, 2, 3, 4] # *** check targets over multiple nodes
        with closing(Context(targets=targets)) as context:
            in_data = self.load_data(context, input_file) # eventually from plugin 
            
            
            for plugin_dict in plugin_list.plugin_list:
    
                print plugin_dict['id']
                logging.debug("Loading plugin %s", plugin_dict['id'])
                plugin = pu.load_plugin(plugin_dict['id'])        
                plugin.set_parameters(plugin_dict['data'])
            
                print "*** creating the output data structure"
                out_data = self.create_data_object(plugin.output_data_type())
                # TODO 
                #out_data = plugin.get_output_data(in_data)
                
                logging.debug("Starting processing  plugin %s", plugin_dict['id'])
                print type(in_data)
                print in_data.data.shape
                print "*** running the plugin"
                plugin.run_plugin(in_data, out_data, processes, process, self)
                print "*** Plugin completed" 
                logging.debug("Completed processing plugin %s", plugin_dict['id'])
                
                out_data.data = self.redistribute_dist_array(in_data, out_data, dist='bnn')
                print out_data.data.shape
                in_data = out_data

        group_name = "process_complete"
        self.output_data(in_data, plugin_list, processing_dir, group_name) 
           
        
    def load_data(self, context, input_file):
        ''' Create a distarray from the specified section of the HDF5 file. '''

        in_data = pu.load_raw_data(input_file)

        #*** temporarily setting dist here - get this from the plugin?
        dist = 'bnn'

        print ("The input filename is", input_file)
        data_key = 'entry1/tomo_entry/instrument/detector/data'
        image_key = 'entry1/tomo_entry/instrument/detector/image_key'

        with h5py.File(input_file, 'r') as f:
            dataset = f[data_key]
            array_shape = dataset.shape
            in_data.image_key = f[image_key][:]

        distribution = Distribution(context, array_shape, dist=dist)
        in_data.data = context.load_hdf5(input_file, distribution=distribution, 
                                    key=data_key)
        
        print "DATA LOADING COMPLETED"        
        return in_data     
                
    # distribute_as() not currently working!
    # *** Incomplete function assuming timeseriescorrection is first?
    # *** i.e. first dist array has all data including dark and flat data
    def redistribute_dist_array(self, old_data, data, dist):
        print "IN REDISTRIBUTE DIST ARRAY"
        
        data.image_key = old_data.image_key        
        if data.current_dist is None:
            shape = data.get_data_shape()
            new_shape = ((shape[0] - len(data.image_key[data.image_key != 0])), shape[1], shape[2])         
            new_dist = Distribution(data.data.context, new_shape, dist)
            #data.data.distribute_as(new_dist)
        else:
            if data.current_dist is not dist:
                new_dist = Distribution(data.data.context, dist)
                #data.data.distribute_as(new_dist)
         
        data.current_dist = dist # set global variable?


    def output_data(self, in_data, plugin_list, processing_dir, group_name):                                  
        output_filename = self.output_plugin_list(in_data, plugin_list, processing_dir)
        print ("outputting to the file", output_filename)
        self.create_output_file(in_data, plugin_list, processing_dir, group_name)
        plugin_list.add_intermediate_data_link(output_filename, in_data, group_name)
        in_data.complete()
        
                        
    def output_plugin_list(self, in_data, plugin_list, processing_dir):
        import time
        filename = os.path.basename(in_data.backing_file.filename)
        filename = os.path.splitext(filename)[0]
        output_filename = os.path.join(processing_dir,"%s_processed_%s.nxs" % 
                                      (filename,time.strftime("%Y%m%d%H%M%S")))

        logging.debug("Running process List.save_list_to_file")
        plugin_list.save_list_to_file(output_filename)
        return output_filename
            
        
    def create_output_file(self, in_data, plugin_list, processing_dir, group_name):

        temp = plugin_list.plugin_list
        final_plugin = temp[len(temp)-1]['id']                
        file_name = os.path.join(processing_dir, "%s_%s.h5" % (plugin_list.name, final_plugin))
        logging.debug("Creating output file %s", file_name)
        in_data.data.context.save_hdf5(file_name, in_data.data, group_name, mode='w')
        

    def create_data_object(self, data_type):
        """Creates an output file of the appropriate type for a specified plugin
    
        :param data_type: Input or output data type for the current plugin
        :type plugin: str
        :returns:  The output data object
        """

        if data_type == RawTimeseriesData:
            return RawTimeseriesData()  
        elif data_type == ProjectionData:
            return ProjectionData()    
        elif data_type == VolumeData:
            return VolumeData()            
        else:
            print "data type undefined in data.transport.distArray.create_data_object()"    
                                
                                    
    def process(self, plugin, data, output, processes, process, params, kernel):

        import numpy as np
        print "*** IN THE PROCESS FUNCTION"
        
        if kernel is "timeseries_correction_set_up":
            kernel = du.timeseries_correction_set_up
        elif kernel is "reconstruction_set_up":
            kernel = du.reconstruction_set_up
        elif kernel is "filter_set_up":
            kernel = du.filter_set_up
        else:
            print("The kernel", kernel, "has not been registered in dist_array_transport")
            sys.exit(1)
         
        iters_key = du.distributed_process(plugin, data, output, processes, 
                                           process, params, kernel)
                                           
        print "*** RETURNING TO THE PROCESS FUNCTION"

        output.data = da.from_localarrays(iters_key[0], 
                                                context=data.data.context, 
                                                dtype=np.int32)    
                                                            
 
        
    def setup(self, path, name):
        return

    def add_data_block(self, name, shape, dtype):
        self.group.create_dataset(name, shape, dtype)

    def get_data_block(self, name):
        return self.group[name]

    def finalise(self):
        if self.backing_file is not None:
            self.backing_file.close()
            self.backing_file = None
