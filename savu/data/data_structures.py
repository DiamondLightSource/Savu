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

import numpy as np

class Data(object):
    """
    The Data class dynamically inherits from relevant data structure classes 
    at runtime and holds the data array.
    """

    def __init__(self, transport):
        self.data = None
        self.add_base(transport)
        self.info = {}


    def add_base(self, ExtraBase):
        cls = self.__class__
        self.__class__ = cls.__class__(cls.__name__, (cls, ExtraBase), {})


    def add_base_classes(self, bases):
        for base in bases:
            self.add_base(base)

        
    def set_pattern(self, dtype, **kargs) :
        if "data_patterns" not in self.info:
            self.info["data_patterns"] = {}
        
        data_dirs = self.info["data_patterns"]
        data_dirs[dtype] = {}
        for args in kargs:
            data_dirs[dtype][args] = kargs[args]


    def set_shape(self, shape):
        self.info['shape'] = shape
        
   
    def get_shape(self):
        return self.info['shape']


    def set_dist(self, dist):
        self.info['dist'] = dist
        
    
    def get_dist(self):
        return self.info["dist"]


    def set_type(self, dtype):
        self.info["type"] = dtype
        
    
    def get_type(self):
        return self.info["type"]


    def get_frame(self, indices, ddirs, name):
        shape = self.get_shape()
        nDims = len(shape)        
        core_dir = ddirs[name]["core_dir"]
        slice_dir = ddirs[name]["slice_dir"]
        
        self.check_dimensions(indices, core_dir, slice_dir, nDims)

        index = [slice(None)]*nDims
        count = 0
        for tdir in slice_dir:
            index[tdir] = slice(indices[count], indices[count]+1, 1)
            count += 1

        return self.data[tuple(index)]


    def check_dimensions(self, indices, core_dir, slice_dir, nDims):
        if len(indices) is not len(slice_dir):
            sys.exit("Incorrect number of indices specified when accessing data.")
        
        if (len(core_dir)+len(slice_dir)) is not nDims:
            sys.exit("Incorrect number of data dimensions specified.")


    def get_sub_shape(self, ddirs, name):
        core_dir = ddirs[name]["core_dir"]
        shape = []
        for core in core_dir:
            shape.append(self.get_shape()[core])
        return tuple(shape)


    def get_dark_and_flat(self):
        if self.get_image_key() is not None:
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
        else:
            sys.exit("Error in get_dark_and_flat(): No image_key found")
            
        return [dark, flat]


    def remove_dark_and_flat(self, data):
        if data.get_image_key() is not None:
            shape = data.get_shape()
            image_key = data.get_image_key()
            new_shape  = shape[0] - len(image_key[image_key != 0])
            return (new_shape, shape[1], shape[2])
        else:
            sys.exit("Error in remove_dark_and_flat(): No image_key found")
        
        
    def check_data_type_exists(self):
        if not isinstance(self, self.get_type()):
            sys.exit("The Data class does not contain an instance of ", self.get_type())
        
        
        
class Raw():

    def __init__(self):
        self.image_key = None

    def set_image_key(self, image_key):
        self.image_key = image_key;

    def get_image_key(self):
        return self.image_key[...]
        
        
class Pattern():

    def get_nPattern(self, slice_dir):
        temp = 1
        for tslice in slice_dir:
            temp *= self.get_shape()[tslice]
        return temp
        
        
    def get_pattern(self, name, indices, data_directions):
        return self.get_frame(indices, data_directions, name)
        
    
    def get_pattern_shape(self, name, data_directions):
        return self.get_sub_shape(data_directions, name)
    

