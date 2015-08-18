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
.. module:: filter
   :platform: Unix
   :synopsis: A base class for all standard filters

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.data.structures import Data
from savu.plugins.plugin import Plugin

from savu.data import structures
from savu.data import utils as du
from savu.core.utils import logmethod
import logging


class Filter(Plugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data
    """

    def __init__(self, name):
        super(Filter,
              self).__init__(name)

    def get_filter_frame_type(self):
        """
        get_filter_frame_type tells the pass through plugin which direction to
        slice through the data before passing it on

         :returns:  the savu.structure core_direction describing the frames to
                    filter
        """
        return structures.CD_PROJECTION

    def get_filter_padding(self):
        """
        Should be overridden to define how wide the frame should be

        :returns:  a dictionary containing the axis to pad in and the amount
        """
        return {}

    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at a time

        :returns:  an integer of the number of frames
        """
        return 8


    def filter_frame(self, data):
        """
        Should be overloaded by filter classes extending this one

        :param data: The data to filter
        :type data: ndarray
        :returns:  The filtered image
        """
        logging.error("filter_frame needs to be implemented for %s",
                      data.__class__)
        raise NotImplementedError("filter_frame needs to be implemented")

    @logmethod
    def process(self, exp, transport, params):
        """
        """
        [in_data, out_data] = self.get_data_obj_list()
        slice_list = du.get_grouped_slice_list(in_data[0], self.get_filter_frame_type(), self.get_max_frames())
        transport.filter_chunk(slice_list, in_data, out_data)

          
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
        
        
    def nInput_datasets(self):
        return 1
         
         
    def nOutput_datasets(self):
        return 1
        