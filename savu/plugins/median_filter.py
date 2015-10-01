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
.. module:: median_3x3_filter
   :platform: Unix
   :synopsis: A plugin to filter each frame with a 3x3 median filter

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.filter import Filter
from savu.plugins.driver.cpu_plugin import CpuPlugin

import scipy.signal.signaltools as sig

from savu.plugins.utils import register_plugin


@register_plugin
class MedianFilter(Filter, CpuPlugin):
    """
    A plugin to filter each frame with a 3x3 median filter

    :param kernel_size: Kernel size for the filter. Default: (1, 3, 3).
    """

    def __init__(self):
        logging.debug("Starting Median Filter")
        super(MedianFilter, self).__init__("MedianFilter")

    def filter_frame(self, data, params):
        logging.debug("Running Filter data")
        result = sig.medfilt(data, self.parameters['kernel_size'])
        return result

    def set_filter_padding(self):
        padding = (self.parameters['kernel_size'][0]-1)/2
        #return {st.CD_PROJECTION:padding} # change this
        return {'0':padding,'1':padding}

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
        in_d1.set_current_pattern_name('PROJECTION') # have changed this to work on the first element of the pattern list rather SINOGRAM, since some datasets don't havea singoram adp
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
        out_d1.set_current_pattern_name('PROJECTION')
        out_d1.set_shape(in_d1.get_shape())
        # set frame chunk
        out_d1.set_nFrames(chunk_size)

        #----------------------------------------------------------------


    def nInput_datasets(self):
        return 1
         
         
    def nOutput_datasets(self):
        return 1
    
    
    def get_max_frames(self):
        return 8
        