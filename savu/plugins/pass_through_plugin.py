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

from savu.data.structures import Data, PassThrough
from savu.data.structures import RawTimeseriesData, ProjectionData, VolumeData
from savu.plugins.plugin import Plugin


class PassThroughPlugin(Plugin):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self, name='PassThroughPlugin'):
        super(PassThroughPlugin, self).__init__(name)

    def populate_default_parameters(self):
        self.parameters['slice_direction'] = 0

    def _process_chunk(self, chunk, data, output, processes, process):
        frames = np.array_split(chunk, processes)[process]

        frame_slice = [slice(None)] * len(data.data.shape)

        for frame in frames:
            frame_slice[self.parameters['slice_direction']] = frame
            projection = data.data[tuple(frame_slice)]
            result = self.process_frame(projection)
            for key in result.keys():
                if key == 'center_of_rotation':
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

    def process(self, data, output, processes, process):
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
        if isinstance(data, ProjectionData):
            # process the data frame by frame
            output.rotation_angle[:] = data.rotation_angle[:]

            # make an array of all the frames to process
            frames = np.arange(data.get_data_shape()
                               [self.parameters['slice_direction']])
            self._process_chunk(frames, data, output, len(processes), process)

        elif isinstance(data, RawTimeseriesData):
            # pass the unchanged data through
            output.rotation_angle[:] = data.rotation_angle[:]
            output.control[:] = data.control[:]

            # process the data frame by frame in chunks
            chunks = data.get_clusterd_frame_list()
            for chunk in chunks:
                self._process_chunk(chunk, data, output, len(processes),
                                    process)
        elif isinstance(data, VolumeData):
            # make an array of all the frames to process
            frames = np.arange(data.get_volume_shape()
                               [self.parameters['slice_direction']])
            self._process_chunk(frames, data, output, len(processes), process)

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
