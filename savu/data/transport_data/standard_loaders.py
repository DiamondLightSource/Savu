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

import numpy as np

import savu.data.data_structures as ds
from savu.data.transport_data.hdf5_transport_data import SliceAlwaysAvailableWrapper


class TomographyLoaders(object):
    """
    This class is called from a tomography loader to use a standard loader. It 
    deals with loading of the data for different formats (e.g. hdf5, tiff,...)
    """
    
    def __init__(self, exp):
        self.loader_setup(exp)


    def loader_setup(self, exp):
        
        base_classes = [ds.Raw]
        exp.info["base_classes"] = base_classes
        data_obj = exp.create_data_object("in_data", "tomo", base_classes)
                
        data_obj.add_pattern("PROJECTION", core_dir = (1, 2), slice_dir = (0,))
        data_obj.add_pattern("SINOGRAM", core_dir = (0, -1), slice_dir = (1,))
        data_obj.add_pattern("VOLUME_XZ", core_dir = (0, 2), slice_dir = (1,))
        
    
    def load_from_nx_tomo(self, exp):
        """
         Define the input nexus file
        
        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        
        data_obj = exp.index["in_data"]["tomo"]

        data_obj.backing_file = h5py.File(exp.info["data_file"], 'r')
        exp.meta_data.set_meta_data("backing_file", data_obj.backing_file)
        logging.debug("Creating file '%s' '%s'", 'tomo_entry', data_obj.backing_file.filename)
        
        data_obj.data = data_obj.backing_file['entry1/tomo_entry/instrument/detector/data']
        data_obj.set_image_key(data_obj.backing_file\
                        ['entry1/tomo_entry/instrument/detector/image_key'])
                        
        exp.meta_data.set_meta_data("image_key", data_obj.get_image_key())
        
        rotation_angle = data_obj.backing_file['entry1/tomo_entry/sample/rotation_angle']
        exp.meta_data.set_meta_data("rotation_angle", rotation_angle[exp.info["image_key"]==0,...])

        control = data_obj.backing_file['entry1/tomo_entry/control/data']
        exp.meta_data.set_meta_data("control", control[...])

        data_obj.set_shape(data_obj.data.shape)
        
        for key in exp.index['in_data'].keys():
            in_data = exp.index["in_data"][key]
            in_data.data = SliceAlwaysAvailableWrapper(in_data.data)
            
