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

    def correction(self, data, image_keys):
        trimmed_data = data[image_keys == 0]
        dark = data[image_keys == 2]
        dark = dark.mean(0)
        dark = np.tile(dark, (trimmed_data.shape[0], 1, 1))
        flat = data[image_keys == 1]
        flat = flat.mean(0)
        flat = np.tile(flat, (trimmed_data.shape[0], 1, 1))
        data = (trimmed_data-dark)/(flat-dark)
        return data

    def process(self, exp, transport):
        in_data, out_data = self.get_datasets(exp)
        transport.timeseries_field_correction(self, in_data, out_data, exp.meta_data)

    def setup(self, experiment):
        """
        Initial setup of all datasets required as input and output to the 
        plugin.  This method is called before the process method in the plugin
        chain.  
        """
        # get all data objects associated with the plugin
        in_data = self.get_in_datasets(experiment)
        out_data = self.get_out_datasets(experiment)

        print in_data[0].meta_data.get_dictionary()
            
        # set details for all input data sets
        in_data[0].in_data_setup(pattern_name='SINOGRAM', 
                                 chunk=self.get_max_frames())

        # set details for all output data sets
        out_data[0].out_data_setup(pattern_name='SINOGRAM',
                                   chunk=self.get_max_frames(),
                                   shape=in_data[0].remove_dark_and_flat())
        # copy or add patterns related to this dataset
        out_data[0].copy_patterns(in_data[0].get_patterns())
        
    def organise_metadata(self, exp):
        in_data, out_data = self.get_datasets(exp)
        
        print "*** in_data dictionary ***"
        for keys in in_data[0].meta_data.get_dictionary().keys():
            print keys
        # copy the entire in_data dictionary
        # If you do not want to copy the whole dictionary pass the key word
        # argument copyKeys = [your list of keys to copy], or alternatively, 
        # removeKeys = [your list of keys to remove]
        # use this function to remove anything you no longer need from the metadata

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 1
