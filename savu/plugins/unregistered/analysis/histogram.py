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
.. module:: histogram
   :platform: Unix
   :synopsis: histograms a binary input

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.plugins.unregistered.analysis.base_analysis import BaseAnalysis
import numpy as np


#@register_plugin
class Histogram(BaseAnalysis, CpuPlugin):

    def __init__(self):
        super(Histogram, self).__init__("Histogram")

    def process_frames(self, data):
        return np.array([data[0].sum()])
    #TODO: probably should add the option for some filtering on the output/ rebinning etc

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()

        # set pattern_name and nframes to process for all datasets
        in_pData[0].plugin_data_setup("CHANNEL", self.get_max_frames())
        sh = in_dataset[0].get_shape()
        axis_labels = ['idx.unit', 'peaks.pixels']
        out_dataset[0].create_dataset(axis_labels=axis_labels,
                                      shape=(sh[-1], 1))
        out_dataset[0].add_pattern("METADATA", slice_dims=(0,), core_dims=(1,))
        out_pData[0].plugin_data_setup("METADATA", self.get_max_frames())

    def get_max_frames(self):
        return 'single'
