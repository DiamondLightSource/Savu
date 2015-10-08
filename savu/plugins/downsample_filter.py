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
.. module:: downsample_filter
   :platform: Unix
   :synopsis: A plugin to filter each frame with a downsample

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class DownsampleFilter(BaseFilter, CpuPlugin):
    """
    A plugin to reduce the data in the selected direction by a proportion

    :param bin_size: Bin Size for the downsample. Default: 2.
    """

    def __init__(self):
        logging.debug("Starting Downsample Filter")
        super(DownsampleFilter,
              self).__init__("DownsampleFilter")

    def get_output_shape(self, input_data):
        input_shape = input_data.get_shape()
        return (input_shape[0],
                (input_shape[1]+1)/self.parameters['bin_size'],
                (input_shape[2]+1)/self.parameters['bin_size'])

    def filter_frame(self, data):
        logging.debug("Running Downsample data")
        result = data[0][:,
                         ::self.parameters['bin_size'],
                         ::self.parameters['bin_size']]
        return result

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
        out_d1.meta_data.copy_dictionary(in_d1.meta_data.get_dictionary())
        # set pattern for this plugin and the shape
        out_d1.set_current_pattern_name("PROJECTION")
        out_d1.set_shape(self.get_output_shape(in_d1))
        # set frame chunk
        out_d1.set_nFrames(chunk_size)

        #----------------------------------------------------------------
        experiment.log(self.name + " End")
