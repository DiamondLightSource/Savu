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
from savu.plugins.cpu_plugin import CpuPlugin

import numpy as np
import logging


class Filter(CpuPlugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data
    """

    def __init__(self, name):
        super(Filter,
              self).__init__(name)

    def _filter_chunk(self, chunk, data, output, processes, process):
        frames = np.array_split(chunk, processes)[process]

        for frame in frames:
            projection = data.data[frame, :, :]
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
            self._filter_chunk(frames, data, output, processes, process)

        elif isinstance(data, RawTimeseriesData):
            # pass the unchanged data through
            output.rotation_angle[:] = data.rotation_angle[:]
            output.control[:] = data.control[:]

            # process the data frame by frame in chunks
            chunks = data.get_clusterd_frame_list()
            for chunk in chunks:
                self._filter_chunk(chunk, data, output, processes, process)
        elif isinstance(data, VolumeData):
            # make an array of all the frames to process
            frames = np.arange(data.get_volume_shape()[0])
            self._filter_chunk(frames, data, output, processes, process)

    def required_resource(self):
        """
        This plugin needs to use the CPU to work

        :returns:  CPU
        """
        return "CPU"

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
