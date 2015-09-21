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
import sys
import logging
import os
import time
import numpy as np

import h5py
from mpi4py import MPI

import savu.plugins.utils as pu

from savu.data.structures import NX_CLASS
from savu.data.TransportMechanism import TransportMechanism
from savu.core.utils import logmethod

def barrier(mpi):
    if mpi is True:
        logging.debug("About to hit a barrier")
        MPI.COMM_WORLD.Barrier()
        logging.debug("Past the barrier")


# TODO tidy up the NeXus format parts of this
class Hdf5Transport(TransportMechanism):

        
    def run_plugin_list(self, input_file, plugin_list, processing_dir, mpi=False,
                     processes=["CPU0"], process=0):
        """Runs a chain of plugins
    
        :param input_data: The input data to give to the chain
        :type input_data: savu.data.structure.
        :param plugin_list: Plugin list.
        :type plugin_list: savu.data.structure.PluginList.
        :param processing_dir: Location of the processing directory.
        :type processing_dir: str.
        :param mpi: Whether this is running in mpi, default is false.
        :type mpi: bool.
        """
        
        input_data = pu.load_raw_data(input_file)

        logging.debug("Running plugin list, just a check")
        filename = os.path.basename(input_data.backing_file.filename)
        filename = os.path.splitext(filename)[0]
        output_filename = \
            os.path.join(processing_dir,
                         "%s_processed_%s.nxs" % (filename,
                                                  time.strftime("%Y%m%d%H%M%S")))
        if process == 0:
            logging.debug("Running process List.save_list_to_file")
            plugin_list.save_list_to_file(output_filename)
    
        in_data = input_data
        output = None
    
        logging.debug("generating all output files")
        files = []
        count = 0
        for plugin_dict in plugin_list.plugin_list:
            logging.debug("Loading plugin %s", plugin_dict['id'])
            plugin = pu.load_plugin(plugin_dict['id'])
    
            # generate somewhere for the data to go
            file_name = os.path.join(processing_dir,
                                     "%s%02i_%s.h5" % (plugin_list.name, count,
                                                       plugin_dict['id']))
            group_name = "%i-%s" % (count, plugin.name)
            barrier(mpi)
            logging.debug("(run_plugin_list) Creating output file after barrier %s", file_name)
            output = pu.create_output_data(plugin, in_data, file_name, group_name,
                                           mpi)
    
            files.append(output)
    
            in_data = output
            count += 1
    
        logging.debug("processing Plugins")
    
        in_data = input_data
        count = 0
        for plugin_dict in plugin_list.plugin_list:
            logging.debug("Loading plugin %s", plugin_dict['id'])
            plugin = pu.load_plugin(plugin_dict['id'])
    
            output = files[count]
    
            plugin.set_parameters(plugin_dict['data'])
    
            logging.debug("Starting processing  plugin %s", plugin_dict['id'])
            plugin.run_plugin(in_data, output, processes, process, self)
            logging.debug("Completed processing plugin %s", plugin_dict['id'])
    
            if in_data is not output:
                in_data.complete()
            in_data = output
    
            if mpi:
                logging.debug("Blocking till all processes complete")
                MPI.COMM_WORLD.Barrier()
    
            if plugin == 0:
                cite_info = plugin.get_citation_information()
                if cite_info is not None:
                    plugin_list.add_plugin_citation(output_filename, count,
                                                      cite_info)
                group_name = "%i-%s" % (count, plugin.name)
                plugin_list.add_intermediate_data_link(output_filename,
                                                        output, group_name)
    
            count += 1
    
        if output is not None:
            output.complete()


    def process(self, plugin, data, output, processes, process, params, kernel):    
        
        if 'reconstruction' in kernel:
            params = [params[0], params[1], data, output, plugin, processes, process]
            self.reconstruction_set_up(params)
        elif 'timeseries' in kernel:
            params = [plugin, processes, process]
            self.timeseries_correction_set_up(data, output, params)
        elif 'filter' in kernel:
            params = [params[0], params[1], processes, process]
            self.filter_set_up()
        else:
            print("Kernel", kernel, "undefined in data.transport.HDF5")
            sys.exit(1)   
            

 
    @logmethod
    def reconstruction_set_up(self, params):
        
        centre_of_rotations = params[0]
        angles = params[1]
        data = params[2]
        output = params[3]
        plugin = params[4]
        processes = params[5]
        process = params[6]
                           
        sinogram_frames = np.arange(data.get_number_of_sinograms())
    
        frames = np.array_split(sinogram_frames, len(processes))[process]
      
    
        for i in range(len(frames)):
            frame_centre_of_rotation = centre_of_rotations[i]
            sinogram = data.data[:, frames[i], :]
            reconstruction = \
                plugin.reconstruct(sinogram, frame_centre_of_rotation, angles,
                                 (output.data.shape[0], output.data.shape[2]),
                                 (output.data.shape[0]/2,
                                  output.data.shape[2]/2))
            output.data[:, frames[i], :] = reconstruction
            plugin.count+=1
            print plugin.count

    
    @logmethod
    def timeseries_correction_set_up(self, data, output, params):

        plugin = params[0]
        processes = params[1]
        process = params[2]
        
        image_key = data.image_key[...]
        # pull out the average dark and flat data
        dark = None
        try:
            dark = np.mean(data.data[image_key == 2, :, :], 0)
        except:
            dark = np.zeros((data.data.shape[1], data.data.shape[2]))
        flat = None
        try:
            flat = np.mean(data.data[image_key == 1, :, :], 0)
        except:
            flat = np.ones((data.data.shape[1], data.data.shape[2]))
        # shortcut to reduce processing
        flat = flat - dark
        flat[flat == 0.0] = 1
        
        # get a list of all the frames
        output_frames = np.arange(data.data.shape[1])
        frames = np.array_split(output_frames, len(processes))[process]

        # The rotation angle can just be pulled out of the file so write that
        rotation_angle = data.rotation_angle[image_key == 0]
        output.rotation_angle[:] = rotation_angle

        for i in frames:
            output.data[:, i, :] = plugin.correction(data.data[image_key == 0, i,:], dark[i,:], flat[i,:])

           
    @logmethod
    def filter_set_up(self, params):    
        param_name = []
        for name in param_name: 
            for p in params:
                globals()[name] = p
        pass
    

    def setup(self, path, name):
        self.backing_file = h5py.File(path, 'w')
        if self.backing_file is None:
            raise IOError("Failed to open the hdf5 file")
        self.group = self.backing_file.create_group(name)
        self.group.attrs[NX_CLASS] = 'NXdata'

    def add_data_block(self, name, shape, dtype):
        self.group.create_dataset(name, shape, dtype)

    def get_data_block(self, name):
        return self.group[name]

    def finalise(self):
        if self.backing_file is not None:
            self.backing_file.close()
            self.backing_file = None
