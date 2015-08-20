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

        dark = np.tile(dark, (data.shape[0], 1))
        flat = np.tile(flat, (data.shape[0], 1))
        data = (data-dark)/flat  # flat = (flat-dark) already calculated for efficiency
        return data
              

    @logmethod
    def process(self, exp, transport, params):
        """
        """
        [in_data, out_data] = self.get_data_objs_list()
        in_data[0].get_slice_list()
        transport.timeseries_field_correction(self, in_data, out_data, 
                                              exp.info, params)


    def setup(self, experiment):
        """
        Initial setup of all datasets required as input and output to the 
        plugin.  This method is called before the process method in the plugin
        chain.  
        """

        chunk_size = self.get_max_frames()
        expInfo = experiment.meta_data

        #-------------------setup input datasets-------------------------

        # get a list of input dataset names required for this plugin
        in_data_list = expInfo.get_meta_data(["plugin_datasets", "in_data"])
        # get all input dataset objects
        in_d1 = experiment.index["in_data"][in_data_list[0]]
        # set all input data patterns
        in_d1.set_current_pattern_name("SINOGRAM")
        # set frame chunk
        in_d1.set_nFrames(chunk_size)

        #----------------------------------------------------------------

        #------------------setup output datasets-------------------------

        # get a list of output dataset names created by this plugin
        out_data_list = expInfo.get_meta_data(["plugin_datasets", "out_data"])

        # create all out_data objects and associated patterns
        # patterns can be copied, added or both
        out_d1 = experiment.create_data_object("out_data", out_data_list[0])        
        out_d1.copy_patterns(in_d1.get_patterns())

        # set pattern for this plugin and the shape
        out_d1.set_current_pattern_name("SINOGRAM")
        out_d1.set_shape(out_d1.remove_dark_and_flat(in_d1))
        # set frame chunk
        out_d1.set_nFrames(chunk_size)

        #----------------------------------------------------------------
                        

    def nInput_datasets(self):
        return 1
         
         
    def nOutput_datasets(self):
        return 1
    
    
    def get_max_frames(self):
        return 8
    