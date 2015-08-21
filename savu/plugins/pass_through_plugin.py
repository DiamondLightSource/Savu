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
.. module:: plugin
   :platform: Unix
   :synopsis: Base class for all plugins used by Savu
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>
"""

import logging

import numpy as np
from savu.data import structures
from savu.data import utils as du
from savu.data.structures import Data, PassThrough
from savu.data.structures import RawTimeseriesData, ProjectionData, VolumeData
from savu.plugins.plugin import Plugin


class PassThroughPlugin(Plugin):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self, name='PassThroughPlugin'):
        super(PassThroughPlugin, self).__init__(name)

    def get_filter_frame_type(self):
        """
        get_filter_frame_type tells the pass through plugin which direction to
        slice through the data before passing it on
         :returns:  the savu.structure core_direction describing the frames to
                    filter
        """
        return structures.CD_PROJECTION

    def get_max_frames(self):
        """
        get_max_frames tells the pass through plugin how many frames to give to 
        the plugins process method at a time, the default is a stack of 8
         :returns:  The number of frames to process per call to process (8)
        """
        return 8

    def _process_chunks(self, slice_list, data, output, processes, process):
        
        process_slice_list = du.get_slice_list_per_process(slice_list, process, processes)

        for sl in process_slice_list:
            projection = data.data[sl]
            result = self.process_frame(projection)
            for key in result.keys():
                if key == 'center_of_rotation':
                    frame = du.get_orthogonal_slice(sl, data.core_directions[self.get_filter_frame_type()])
                    output.center_of_rotation[frame] = result[key]

    def process_frame(self, data):
        """
        Should be overloaded by filter classes extending this one
        :param data: The data to filter
        :type data: ndarray
        :returns:  The filtered image
        """
        logging.error("filter_frame needs to be implemented for %s",
                      data.__class__)
        raise NotImplementedError("filter_frame needs to be implemented")

    def process(self, data, output, processes, process, transport):
        """
        This method is called after the plugin has been created by the
        pipeline framework
        :param data: The input data object.
        :type data: savu.data.structures
        :param data: The output data object
        :type data: savu.data.structures
        :param processes: The number of processes which will be doing the work
        :type path: int
        :param path: The specific process which we are
        :type path: int
        """
        slice_list = du.get_grouped_slice_list(data, self.get_filter_frame_type(), self.get_max_frames())
        self._process_chunks(slice_list, data, output, len(processes), process)

    def required_data_type(self):
        """
        The input for this plugin is Data
        :returns:  Data
        """
        return Data

    def output_data_type(self):
        """
        The output of this plugin is Data
        :returns:  Data
        """
        return PassThrough

    def input_dist(self):
        """
        The input DistArray distribution for this plugin is "nbn"
        (i.e. block in the second dimension)
        :returns:  DistArray distribution
        """
        return "bnn"

    def output_dist(self):
        """
        The output DistArray distribution for this plugin is "nbn"
        (i.e. block in the second dimension)
        :returns:  DistArray distribution
        """
        return "bnn"
        