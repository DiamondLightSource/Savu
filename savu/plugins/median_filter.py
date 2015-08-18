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

from savu.data import structures as st

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

    def get_filter_padding(self):
        padding = (self.parameters['kernel_size'][0]-1)/2
        return {st.CD_PROJECTION:padding}

    def filter_frame(self, data):
        logging.debug("Running Filter data")
        result = sig.medfilt(data, self.parameters['kernel_size'])
        return result

          
    def setup(self, experiment):

        #-------------------setup input datasets-------------------------

        # get a list of input dataset names required for this plugin
        in_data_list = experiment.info["plugin_datasets"]["in_data"]
        
        # get all input dataset objects
        in_d1 = experiment.index["in_data"][in_data_list[0]]
        
        # set all input data patterns
        in_d1.set_pattern_name("SINOGRAM")

        #-------------------------------------------------------------

        #------------------setup output datasets-------------------------

        # get a list of output dataset names created by this plugin
        out_data_list = experiment.info["plugin_datasets"]["out_data"]

        # create all out_data objects and associated patterns
        # patterns can be copied, added or both
        out_d1 = experiment.create_data_object("out_data", out_data_list[0])
        out_d1.copy_patterns(in_d1.info["data_patterns"])

        # set pattern for this plugin and the shape
        out_d1.set_pattern_name("VOLUME_XZ")
        shape = in_d1.get_shape()
        out_d1.set_shape((shape[2], shape[1], shape[2]))

        #------------------------------------------------------------- 