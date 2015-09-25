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
import numpy as np
import dezing

from savu.plugins.filter import Filter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.data.data_structures import Padding
from savu.plugins.utils import register_plugin

@register_plugin
class DezingFilter(Filter, CpuPlugin):
    """
    A plugin
    
    :param outlier_mu: Magnitude of parameter for detecting outlier. Default: 10.0.
    :param kernel_size: Number of frames included in average. Default: 5. 
    """

    def __init__(self):
        logging.debug("Starting Dezinger Filter")
        super(DezingFilter,
              self).__init__("DezingFilter")

    def pre_process(self, exp):
        in_data = self.get_data_objects(exp.index, "in_data")[0]
        data_size = in_data.get_shape()
        logging.debug("Running Dezing Setup")
        self.padding  = (self.parameters['kernel_size']-1)/2
        dezing.setup_size(data_size,self.parameters['outlier_mu'],self.padding)
        logging.debug("Finished Dezing Setup")

    def post_process(self):
        logging.debug("Running Dezing Cleanup")
        dezing.cleanup()
        logging.debug("Finished Dezing Cleanup")

    def set_filter_padding(self, in_data):
        padding = Padding(in_data[0].get_current_pattern())
        padding.pad_multi_frames(self.padding)
        padding.pad_frame_edges(self.padding)
        in_data[0].padding = padding.get_padding_directions()

    def filter_frame(self, data, params):
        logging.debug("Running Dezing Frame")
        result=np.empty_like(data[0])
        dezing.run(data[0],result)
        logging.debug("Finished Dezing Frame")
        return result


        