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
.. module:: Timeseries_field_corrections
   :platform: Unix
   :synopsis: A Plugin to apply a simple dark and flatfield correction to some
       raw timeseries data

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.plugin import Plugin
from savu.core.utils import logmethod

import numpy as np

from savu.plugins.utils import register_plugin


@register_plugin
class TimeseriesFieldCorrections(Plugin, CpuPlugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data    
    :param in_datasets: Create a list of the dataset(s) to process. Default: [].
    :param out_datasets: Create a list of the dataset(s) to process. Default: [].

    """

    def __init__(self):
        super(TimeseriesFieldCorrections,
              self).__init__("TimeseriesFieldCorrections")
              
              
    def correction(self, data, dark, flat, params):
        dark = np.tile(dark, (data.shape[0], 1, 1))
        flat = np.tile(flat, (data.shape[0], 1, 1))
        data = (data-dark)/flat  # flat = (flat-dark) already calculated for efficiency
        return data
              

#    @logmethod
#    def process(self, exp, transport, params):
#        """
#        """
#        in_data = self.get_data_objects(exp.index, "in_data")
#        out_data = self.get_data_objects(exp.index, "out_data")
#        transport.timeseries_field_correction(self, in_data, out_data, exp.meta_data, params)


    def process(self, exp, transport, params):
        
        in_data = self.get_data_objects(exp.index, "in_data")
        out_data = self.get_data_objects(exp.index, "out_data")
        transport.timeseries_field_correction(self, in_data, out_data, exp.meta_data, params)
#
#        in_data = in_data[0]
#        out_data = out_data[0]
#                
#        print in_data.backing_file
#        print out_data.backing_file                
#                
#        print "performing the processing"
#        slice_list = in_data.get_slice_list()
#        for sl in slice_list:
#            temp = in_data.data[sl]
#            out_data.data[sl] = temp



    def setup(self, experiment):
        """
        Initial setup of all datasets required as input and output to the 
        plugin.  This method is called before the process method in the plugin
        chain.  
        """

        chunk_size = self.get_max_frames()

        #-------------------setup input datasets-------------------------

        # get a list of input dataset names required for this plugin
        in_data_list = self.parameters["in_datasets"]
        # get all input dataset objects
        in_d1 = experiment.index["in_data"][in_data_list[0]]
        # set all input data patterns
        in_d1.set_current_pattern_name("SINOGRAM")
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
        #be removed since out_data is no longer an instance of TomoRaw)
        # If you do not want to copy the whole dictionary pass the key word
        # argument copyKeys = [your list of keys to copy], or alternatively, 
        # removeKeys = [your list of keys to remove]
        out_d1.meta_data.copy_dictionary(in_d1.meta_data.get_dictionary(), rawFlag=True)

        # set pattern for this plugin and the shape
        out_d1.set_current_pattern_name("SINOGRAM")
        out_d1.set_shape(in_d1.remove_dark_and_flat())
        # set frame chunk
        out_d1.set_nFrames(chunk_size)

        #----------------------------------------------------------------
                        

    def nInput_datasets(self):
        return 1
         
         
    def nOutput_datasets(self):
        return 1
    
    
    def get_max_frames(self):
        return 8
    
