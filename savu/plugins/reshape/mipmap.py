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
.. module:: mipmaping plugin (pyramid-like data downampling)
   :platform: Unix
   :synopsis: A plugin to downsample multidimensional data 

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy
import skimage.measure as skim

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class Mipmap(Plugin, CpuPlugin):
    """
    A plugin to downsample multidimensional data based on a tuple of provided levels
    
    :u*param scales_list: A list of scales to downsample the data. Default: (2,2).
    :u*param mode: One of 'mean', 'median', 'min', 'max'. Default: 'mean'.
    :u*param pattern: One of. Default: 'VOLUME_XZ'.
    :param out_datasets: Default out dataset names. Default: ['raw', 'two_x_two']
    """

    def __init__(self):
        logging.debug("Starting Mipmapping")
        super(Mipmap,
              self).__init__("Mipmap")
        self.out_shape = None
        self.mode_dict = { 'mean'  : numpy.mean,
                           'median': numpy.median,
                           'min'   : numpy.min,
                           'max'   : numpy.max }
        self.mapsnumber = None

    def get_number_of_output_datasets(self):
        self.mapmap_scales = self.parameters['scales_list']
        # the number of mipmap maps
        try:
            self.mapsnumber = len(self.mapmap_scales)
        except TypeError:
            self.mapsnumber = 1
            
        return self.mapsnumber

    def setup(self):
        mapsnumber = self.get_number_of_output_datasets()
        
        # get all in and out datasets required by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # get plugin specific instances of these datasets
        in_pData, out_pData = self.get_plugin_datasets()

        plugin_pattern = self.parameters['pattern']
        in_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())
        
        
        for i in range(0,mapsnumber):
            self.out_shape = \
            self.new_shape(in_dataset[0].get_shape(), in_dataset[0], i)
            out_dataset[i].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=self.out_shape)
            out_pData[i].plugin_data_setup(plugin_pattern, self.get_max_frames())

    def new_shape(self, full_shape, data, ind):
        core_dirs = data.get_core_dimensions()
        self.mapmap_scales = self.parameters['scales_list']
        new_shape = list(full_shape)
        if ((ind == 0) and (self.mapsnumber > 1)):
            for dim in core_dirs:
                new_shape[dim] = full_shape[dim]/self.mapmap_scales[ind]
                if (full_shape[dim] % self.mapmap_scales[ind]) > 0:
                    new_shape[dim] += 1
        elif ((ind == 1) and (self.mapsnumber > 1)):
            for dim in core_dirs:
                new_shape[dim] = full_shape[dim]/(self.mapmap_scales[ind-1]*self.mapmap_scales[ind])
                if (full_shape[dim] % (self.mapmap_scales[ind-1]*self.mapmap_scales[ind])) > 0:
                    new_shape[dim] += 1
        else:
            for dim in core_dirs:
                new_shape[dim] = full_shape[dim]/self.mapmap_scales
                if (full_shape[dim] % self.mapmap_scales) > 0:
                    new_shape[dim] += 1
        return tuple(new_shape)

    def process_frames(self, data):
        logging.debug("Running Mipmapping")
        if self.parameters['mode'] in self.mode_dict:
            sampler = self.mode_dict[self.parameters['mode']]
        else:
            logging.warning("Unknown downsample mode. Using 'mean'.")
            sampler = numpy.mean
        if (self.mapsnumber == 1):
            block_size = (self.mapmap_scales, self.mapmap_scales)
            result = skim.block_reduce(data[0], block_size, sampler)
        elif (self.mapsnumber == 2):
            #generate various block sizes
            block_size = (self.mapmap_scales[0], self.mapmap_scales[0])
            result1 = skim.block_reduce(data[0], block_size, sampler)
            block_size = (self.mapmap_scales[0]*self.mapmap_scales[1], self.mapmap_scales[0]*self.mapmap_scales[1])
            result2 = skim.block_reduce(data[0], block_size, sampler)
            result = [result1,result2]
        else:
            raise("The number of given maps is too high ")
        return result
    
    """
    def get_output_shape(self, input_data):
        input_shape = input_data.get_shape()
        core_dirs = input_data.get_core_directions()
        output_shape = []
        for i in range(len(input_shape)):
            if i in core_dirs:
                output_shape.append(input_shape[i]/self.mapmap_scales[0])
            else:
                output_shape.append(input_shape[i])
        
        return output_shape
    """

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return self.get_number_of_output_datasets()

    def get_max_frames(self):
        # This filter processes one frame at a time
        return 'single'
