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
from savu.data.structures import RawTimeseriesData, ProjectionData, VolumeData
from savu.plugins.plugin import Plugin

import numpy as np
import logging


class Filter(Plugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data
    """

    def __init__(self, name):
        super(Filter,
              self).__init__(name)

    def get_filter_width(self):
        """
        Should be overridden to define how wide the frame should be

        :returns:  The width of the frame to be filtered
        """
        return 0

    def _filter_chunk(self, chunk, data, output, processes, process):
        frames = np.array_split(chunk, processes)[process]

        width = self.get_filter_width()
        for frame in frames:
            minval = frame-width
            maxval = frame+width+1
            minpad = 0
            maxpad = 0
            if minval < 0:
                minpad = minval*-1
                minval = 0
            if maxval > data.data.shape[0]:
                maxpad = (maxval-data.data.shape[0]) + 1
                maxval = data.data.shape[0] - 1
            projection = data.data[minval:maxval, :, :]
            logging.debug("projection shape is %s", str(projection.shape))
            logging.debug("max and min are %i, %i", minval, maxval)
            projection = np.pad(projection, ((minpad, maxpad), (0, 0), (0, 0)),
                                mode='edge')
            result = self.filter_frame(projection)
            output.data[frame, :, :] = result

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
        if isinstance(data, ProjectionData):
            # process the data frame by frame
            output.rotation_angle[:] = data.rotation_angle[:]

            # make an array of all the frames to process
            frames = np.arange(data.get_number_of_projections())
            self._filter_chunk(frames, data, output, len(processes), process)

        elif isinstance(data, RawTimeseriesData):
            # pass the unchanged data through
            output.rotation_angle[:] = data.rotation_angle[:]
            output.control[:] = data.control[:]

            # process the data frame by frame in chunks
            chunks = data.get_clusterd_frame_list()
            for chunk in chunks:
                self._filter_chunk(chunk, data, output, len(processes),
                                   process)
        elif isinstance(data, VolumeData):
            # make an array of all the frames to process
            frames = np.arange(data.get_volume_shape()[0])
            self._filter_chunk(frames, data, output, len(processes), process)

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
