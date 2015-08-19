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
.. module:: standard_loaders
   :platform: Unix
   :synopsis: Classes for different experimental setups containing standard
   data loaders.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import h5py
import logging

from mpi4py import MPI
import numpy as np

import savu.data.data_structures as ds

NX_CLASS = 'NX_class'

class TomographySavers(object):
    """
    This class is called from a tomography loader when using a standard saver. 
    It deals with saving of the data to different standard formats
    """
    
    def __init__(self, exp, params):
        self.saver_setup(exp)
        self.parameters = params

    def saver_setup(self, exp):
        pass
    

    def save_to_hdf5(self, exp):
        dtype = np.float32 #*** changed from double
        for key in exp.index["out_data"].keys():
            out_data = exp.index["out_data"][key]
            out_data.backing_file = self.create_backing_h5(key, exp.info)
            group = self.create_entries(out_data.backing_file, out_data, exp.info, key, dtype)
    
            self.output_meta_data(group, out_data, exp.info, dtype)


    def create_backing_h5(self, key, info):
        """
        Create a h5 backend for output data
        """
        filename = info["filename"][key]
        if info["mpi"] is True:
            backing_file = h5py.File(filename, 'w', driver='mpio', 
                                                         comm=MPI.COMM_WORLD)
        else:
            backing_file = h5py.File(filename, 'w')

        if backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        logging.debug("Creating file '%s' '%s'", info["group_name"], 
                                                         backing_file.filename)
        
        return backing_file
        

    def create_entries(self, backing_file, data, info, key, dtype):
        from savu.data.transport_data.hdf5_transport_data import SliceAvailableWrapper
        group = backing_file.create_group(info["group_name"][key])
        group.attrs[NX_CLASS] = 'NXdata'

        params = self.set_name("data_value")
        self.output_data_to_file(group, params, data.get_shape(), dtype)        
        data.data = SliceAvailableWrapper(params['name2'], params['name1'])
        return group


    def output_meta_data(self, group, data, info, dtype):
        output_list = self.get_output_list(info, data)

    #dt = h5py.special_dtype(vlen=str)

        for key in info.keys():
            ttype = type(info[key])
            if ttype is list:
                print info[key]

        for name in output_list:
            params = self.set_name(name)
            value = info[name]
            [shape, dtype] = self.get_type(value)
            # calculate shape
            # determine type            
            
            self.output_data_to_file(group, params)#, info[name].shape, dtype)
            params['name1'][...] = value
        

    def get_output_list(self, info, data):
        if self.parameters is False:           
            pattern = data.get_pattern_name()
            if isinstance(data, ds.Raw):
                pattern = "RAW"
            return self.get_pattern_meta_data(data, pattern)
        else:
            meta_data = []
            for key in info.keys():
                meta_data.append(key)
            return meta_data
        

    # temporary need to move this somewhere else        
    def get_pattern_meta_data(self, pattern):
        theDict = {}
        theDict['RAW'] = ["image_key", "control", "rotation_angle"] # *** ADD COR
        theDict['PROJECTION'] = ["rotation_angle"]
        theDict['SINOGRAM'] = theDict['PROJECTION']
        
        try:
            return theDict['pattern']
        except KeyError:
            print "Warning: No meta_data output is associated with the \
                                                            pattern:", pattern
            return []
        
        
    def output_data_to_file(self, group, params, shape, dtype):
        
        params['name1'] = group.create_dataset(params['name1'], shape, dtype)
        params['name1'].attrs['signal'] = 1
        params['name2'] = group.create_dataset(params['name2'], shape, np.bool_)


    def set_name(self, name):
        params = {}
        params['name1'] = name
        params['name2'] = name + "_avail"
        return params

