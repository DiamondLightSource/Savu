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
.. module:: filter
   :platform: Unix
   :synopsis: A base class for all standard filters

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin

from savu.core.utils import logmethod
import logging


class Filter(Plugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data
            
    :param in_datasets: Create a list of the dataset(s) to process. Default: [].
    :param out_datasets: Create a list of the dataset(s) to process. Default: [].

    """

    def __init__(self, name):
        super(Filter, self).__init__(name)

    def set_filter_padding(self, in_data, out_data):
        """
        Should be overridden to define how wide the frame should be for each 
        input data set
        """
        return {}

    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at a time

        :returns:  an integer of the number of frames
        """
        return 8

    def filter_frame(self, data):
        """
        Should be overloaded by filter classes extending this one

        :param data: The data to filter
        :type data: ndarray
        :returns:  The filtered image
        """
        logging.error("filter_frame needs to be implemented for %s",
                      data.__class__)
        raise NotImplementedError("filter_frame needs to be implemented")


    @logmethod
    def process(self, exp, transport):
        """
        """
        in_data = self.get_data_objects(exp.index, "in_data")
        out_data = self.get_data_objects(exp.index, "out_data")
        self.set_filter_padding(in_data, out_data)
        transport.filter_chunk(self, in_data, out_data, exp.meta_data)
        # reset padding to none
        for data in in_data:
            data.padding = None

          
    def setup(self, experiment):

        experiment.log(self.name + " Start")
        chunk_size = self.get_max_frames()

        #-------------------setup input datasets-------------------------

        # get a list of input dataset names required for this plugin
        in_data_list = self.parameters["in_datasets"]
        # get all input dataset objects
        in_d1 = experiment.index["in_data"][in_data_list[0]]        
        # set all input data patterns
        in_d1.set_current_pattern_name("PROJECTION")
        # set frame chunk
        in_d1.set_nFrames(chunk_size)
        
        #----------------------------------------------------------------

        #------------------setup output datasets-------------------------

        # get a list of output dataset names created by this plugin
        out_data_list = self.parameters["out_datasets"]
        
        # create all out_data objects and associated patterns and meta_data
        # patterns can be copied, added or both
        out_d1 = experiment.create_data_object("out_data", out_data_list[0])
        
        out_d1.copy_patterns(in_d1.get_patterns())
        # copy the entire in_data dictionary (image_key, dark and flat will 
        # be removed since out_data is no longer an instance of TomoRaw)
        # If you do not want to copy the whole dictionary pass the key word
        # argument copyKeys = [your list of keys to copy], or alternatively, 
        # removeKeys = [your list of keys to remove]
        out_d1.meta_data.copy_dictionary(in_d1.meta_data.get_dictionary())

        # set pattern for this plugin and the shape
        out_d1.set_current_pattern_name("PROJECTION")
        #out_d1.set_shape(in_d1.remove_dark_and_flat())
        out_d1.set_shape(in_d1.get_shape())
        # set frame chunk
        out_d1.set_nFrames(chunk_size)

        #----------------------------------------------------------------
        experiment.log(self.name + " End")
        
    def nInput_datasets(self):
        return 1
         
         
    def nOutput_datasets(self):
        return 1
        