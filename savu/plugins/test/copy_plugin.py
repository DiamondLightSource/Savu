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
.. module:: A null pluigin which does nothing but copies a data block projection wise
   :platform: Unix
   :synopsis: A null pluigin which does nothing but copies a data block projection wise

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.filter import Filter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.data import structures

from savu.plugins.utils import register_plugin


@register_plugin
class CopyPlugin(Filter, CpuPlugin):
    """
    A plugin to copy data with no opperation, for testing only

    :param number_of_frames: Number of frames to load at a time. Default: 1.
    :param copy_direction: Direction to load and save data (proj|sino|pattern). Default: "proj".
    """

    def __init__(self):
        logging.debug("Starting Copy plugin")
        super(CopyPlugin,
              self).__init__("CopyPlugin")

    def get_filter_frame_type(self):
        """
        get_filter_frame_type tells the pass through plugin which direction to
        slice through the data before passing it on

         :returns:  the savu.structure core_direction describing the frames to
                    filter
        """
        if self.parameters['copy_direction'] == "proj":
            logging.debug("Copy Plugin direction set to Projection")
            return structures.CD_PROJECTION
        elif self.parameters['copy_direction'] == "sino":
            logging.debug("Copy Plugin direction set to Sinogram")
            return structures.CD_SINOGRAM
        elif self.parameters['copy_direction'] == "pattern":
            logging.debug("Copy Plugin direction set to Pattern")
            return structures.CD_PATTERN
        return structures.CD_PROJECTION

    def get_max_frames(self):
        """
        :returns:  an integer of the number of frames
        """
        logging.debug("Number of frames is set to %i" % self.parameters['number_of_frames'])
        return self.parameters['number_of_frames']

    def filter_frame(self, data, params):
        logging.debug("Running Copy Frame")
        return data[0]
