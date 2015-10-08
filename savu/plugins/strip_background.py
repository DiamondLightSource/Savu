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
.. module:: Background subtraction plugin
   :platform: Unix
   :synopsis: A plugin to automatically strip peaks and subtract background

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""
import logging
from scipy.signal import savgol_filter
import numpy as np
from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class StripBackground(BaseFilter, CpuPlugin):
    """
    1D background removal. PyMca magic function
    
    :param iterations: Number of iterations. Default: 100.
    :param window: Half width of the rolling window. Default: 10.
    :param SG_filter_iterations: How many iterations until smoothing occurs. Default: 5.
    :param SG_width: Whats the savitzgy golay window. Default: 35.
    :param SG_polyorder: Whats the savitzgy-golay poly order. Default: 5.

    """

    def __init__(self):
        logging.debug("Stripping background")
        super(StripBackground, self).__init__("StripBackground")

    def get_filter_padding(self):
        return {}
    
    def get_max_frames(self):
        return 1
    
    def filter_frame(self, data, params):
        its=self.parameters['iterations']
        w=self.parameters['window']
        smoothed=self.parameters['SG_filter_iterations']
        SGwidth=self.parameters['SG_width']
        SGpoly=self.parameters['SG_polyorder']
        data = np.squeeze(data)
        npts = len(data)
        filtered = savgol_filter(data,SGwidth,SGpoly)
        aved = np.zeros_like(filtered)
        for k in range(its):
            for i in range(npts):
                if (i-w)<0:
                    aved[i] = (filtered[i] + filtered[i+w])/2.
                elif (i+w)>(len(data)-1):
                    aved[i] = (filtered[i] + filtered[i-w])/2.
                else:
                    aved[i] = (filtered[i-w] + filtered[i] + filtered[i+w])/3.
            filtered[aved<filtered] = aved[aved<filtered]
            if not (k/float(smoothed)-k/int(smoothed)):
                filtered=savgol_filter(filtered,SGwidth,SGpoly)
        return data-filtered
    
    def setup(self, experiment):

        chunk_size = self.get_max_frames()

        #-------------------setup input datasets-------------------------

        # get a list of input dataset names required for this plugin
        in_data_list = self.parameters["in_datasets"]
        # get all input dataset objects
        in_d1 = experiment.index["in_data"][in_data_list[0]]
        # set all input data patterns
        in_d1.set_current_pattern_name("SPECTRUM") # we take in a pattern
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
        out_d1.set_current_pattern_name("SPECTRUM")# output a spectrum

        # set frame chunk
        out_d1.set_nFrames(chunk_size)
