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
.. module:: data_structures
   :platform: Unix
   :synopsis: Contains the Data class and all the data structures from which 
   Data can inherit. 

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import sys
import logging

import numpy as np

from savu.data.meta_data import MetaData


class Pattern(object):

    def __init__(self):
        self.meta_data_setup()

        
    def meta_data_setup(self):
        pattern_list = self.set_available_pattern_list()
        self.meta_data.set_meta_data("pattern_list", pattern_list)
        self.meta_data.set_meta_data("nFrames", 1)
        self.meta_data.set_meta_data("name", None)
        self.meta_data.set_meta_data("data_patterns", {})

        
    def set_available_pattern_list(self):
        pattern_list = ["SINOGRAM", 
                        "PROJECTION",
                        "VOLUME_YZ",
                        "VOLUME_XZ", 
                        "VOLUME_XY",
                        "SPECTRUM"] # added spectrum adp 17th August
        return pattern_list                        
                
                
    def get_available_pattern_list(self):
        return self.meta_data.get_meta_data("pattern_list")
        
    
    def add_pattern(self, dtype, **kargs):
        if dtype in self.get_available_pattern_list():            
            data_dirs = self.get_patterns()
            data_dirs[dtype] = {}
            for args in kargs:
                data_dirs[dtype][args] = kargs[args]
        else:
            errorMsg = "The data pattern " + dtype + " does not exist.  Please choose " + \
            " from the following list: \n" + str(self.get_available_pattern_list())
            sys.exit(errorMsg)


    def get_patterns(self):
        return self.meta_data.get_meta_data("data_patterns")


    def get_nPattern(self):
        temp = 1
        slice_dir = self.get_patterns()[self.get_pattern_name()]["slice_dir"]
        for tslice in slice_dir:
            temp *= self.get_shape()[tslice]
        return temp
        
        
    def copy_patterns(self, patterns):
        self.meta_data.set_meta_data("data_patterns", patterns)


    def add_volume_patterns(self):
        self.add_pattern("VOLUME_YZ", core_dir = (1, 2), slice_dir = (0,))
        self.add_pattern("VOLUME_XZ", core_dir = (0, 2), slice_dir = (1,))
        self.add_pattern("VOLUME_XY", core_dir = (0, 1), slice_dir = (2,))
        
    
    def set_current_pattern_name(self, name):
        self.meta_data.set_meta_data("name", name)
        self.check_data_type_exists()
               

    def get_current_pattern_name(self):
        name = self.meta_data.get_meta_data("name")
        if name is not None:
            return name
        else:
            raise Exception("The pattern name has not been set.")


    def get_pattern_shape(self):
        return self.get_sub_shape(self.get_current_pattern_name())


    def check_dimensions(self, indices, core_dir, slice_dir, nDims):
        if len(indices) is not len(slice_dir):
            sys.exit("Incorrect number of indices specified when accessing data.")
        
        if (len(core_dir)+len(slice_dir)) is not nDims:
            sys.exit("Incorrect number of data dimensions specified.")


    def check_data_type_exists(self):
        if self.get_current_pattern_name() not in self.get_available_pattern_list():
            raise Exception(("Error: The Data class does not contain an \
                        instance of ", self.get_current_pattern_name()))

            
    def set_nFrames(self, nFrames):
        self.meta_data.set_meta_data("nFrames", nFrames)
        
        
    def get_nFrames(self, nFrames):
        self.meta_data.get_meta_data("nFrames")


    def get_frame(self, indices):
        index = self.get_index(indices)
        return np.squeeze(self.data[index])


    def get_index(self, indices):
        shape = self.get_shape()
        nDims = len(shape)      
        name = self.get_pattern_name()
        ddirs = self.info["data_patterns"]
        core_dir = ddirs[name]["core_dir"]
        slice_dir = ddirs[name]["slice_dir"]

        self.check_dimensions(indices, core_dir, slice_dir, nDims)

        index = [slice(None)]*nDims
        count = 0
        for tdir in slice_dir:
            index[tdir] = slice(indices[count], indices[count]+1, 1)
            count += 1

        return tuple(index)


    def get_sub_shape(self, name):
        core_dir = self.info["data_patterns"][name]["core_dir"]
        shape = []
        for core in core_dir:
            shape.append(self.get_shape()[core])
        return tuple(shape)
        
        
class Data(Pattern):
    """
    The Data class dynamically inherits from relevant data structure classes 
    at runtime and holds the data array.
    """

    def __init__(self, transport):
        self.meta_data = MetaData()
        super(Data, self).__init__()
        self.backing_file = None
        self.data = None
        self.add_base(transport)
    
    
    def __deepcopy__(self, memo):
        return self


    def add_base(self, ExtraBase):
        cls = self.__class__
        self.__class__ = cls.__class__(cls.__name__, (cls, ExtraBase), {})
        ExtraBase().__init__()


    def add_base_classes(self, bases):
        for base in bases:
            self.add_base(base)


    def set_shape(self, shape):
        self.meta_data.set_meta_data('shape', shape)
        
   
    def get_shape(self):
        return self.meta_data.get_meta_data('shape')


    def set_dist(self, dist):
        self.meta_data.set_meta_data('dist', dist)
        
    
    def get_dist(self):
        return self.meta_data.get_meta_data('dist')

        
    def remove_dark_and_flat(self, data):
        if data.get_image_key() is not None:
            shape = data.get_shape()
            image_key = data.get_image_key()
            new_shape  = shape[0] - len(image_key[image_key != 0])
            return (new_shape, shape[1], shape[2])
        else:
            logging.warn("Error in remove_dark_and_flat(): No image_key found")
            shape = data.get_shape()
            return (shape, shape[1], shape[2])#Mark Corrected 17th August
        
        
        
class Raw(object):

    def __init__(self):
        self.image_key = None
        self.image_key_slice = None


    def set_image_key(self, image_key):
        self.image_key = image_key;
        self.set_image_key_slice()
        self.get_dark_and_flat()


    def get_image_key(self):
        try:
            return self.image_key[...]
        except:
            return None
                        
                        
    def set_image_key_slice(self):
        image_key_bool = self.get_image_key() == 0
        image_key_index = np.where(image_key_bool)[0]
        start = image_key_index[0]
        end = image_key_index[-1]
        self.image_key_slice = slice(start, end + 1, 1)


    def get_image_key_slice(self):
        return self.image_key_slice
                                                

    def get_dark_and_flat(self):
        dark = None
        try:
            dark = np.mean(self.data[self.get_image_key() == 2, :, :], 0)
        except:
            print "Setting the dark data to zero"
            dark = np.zeros((self.get_shape()[1], self.get_shape()[2]))

        flat = None
        try:
            flat = np.mean(self.data[self.get_image_key() == 1, :, :], 0)
        except:
            print "Setting the light data to one"
            flat = np.ones((self.get_shape()[1], self.get_shape()[2]))

        # shortcut to reduce processing
        flat = flat - dark
        flat[flat == 0.0] = 1

        self.meta_data.set_meta_data("dark", dark)
        self.meta_data.set_meta_data("flat", flat)
        
        
    def get_frame_raw(self, indices):
        index = self.get_index(indices)
        temp = []
        for i in index:
            temp.append(i)
        direction = self.info["data_patterns"][self.get_pattern_name()]["core_dir"][0]
        temp[direction] = self.get_image_key_slice()
        return np.squeeze(self.data[tuple(temp)])
        

        
