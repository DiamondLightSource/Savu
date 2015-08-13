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
        in_data = exp.index["in_data"]["tomo"]
        out_data = exp.index["out_data"]["tomo"]
        transport.timeseries_field_correction(self, in_data, out_data, 
                                              exp.info, params)


    def setup(self, experiment):
        
        # set all in_data objects required in this plugin 
        experiment.meta_data.set_plugin_objects("in_data", ["tomo"])
        # for each of the required in_data objects...
        # get the in_data object and set the required in_data pattern.
        in_data = experiment.index["in_data"]["tomo"]
        in_data.set_pattern_name("SINOGRAM")
        # check the in_data type exists        
        in_data.check_data_type_exists()
        
        # set all in_data objects required in this plugin 
        experiment.meta_data.set_plugin_objects("out_data", ["tomo"])
        # for each of the required out_data objects...
        # create the out_data object and set the pattern and shape
        out_data = experiment.create_data_object("out_data", "tomo")
        out_data.copy_patterns(in_data.info["data_patterns"])
        out_data.set_shape(out_data.remove_dark_and_flat(in_data))
        out_data.set_pattern_name("SINOGRAM") # already know this exists

        
     