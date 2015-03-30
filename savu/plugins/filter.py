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

    def _filter_chunk(self, slice_list, data, output, processes, process):
        logging.debug("Running filter._filter_chunk")
        process_slice_list = du.get_slice_list_per_process(slice_list, process, processes)

        padding = self.get_filter_padding()

        for sl in process_slice_list:
            section = du.get_padded_slice_data(sl, padding, data)
            result = self.filter_frame(section)
            output.data[sl] = du.get_unpadded_slice_data(sl, padding, data, result)

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

    def process(self, data, output, processes, process):
        """
        """
        slice_list = du.get_grouped_slice_list(data, self.get_filter_frame_type(), self.get_max_frames())
        self._filter_chunk(slice_list, data, output, len(processes), process)

    def required_data_type(self):
        """
        The input for this plugin is RawTimeseriesData

        :returns:  Data
        """
        return Data

    def output_data_type(self):
        """
        The output of this plugin is ProjectionData

        :returns:  Data
        """
        return Data
