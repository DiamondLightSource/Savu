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
from savu.plugins.plugin import Plugin

from savu.core.utils import logmethod
import logging


class Filter(Plugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data

    :param in_datasets: Create a list of the dataset(s) to process. Default: [].
    :param out_datasets: Create a list of the dataset(s) to process. Default: [].

    """

    def __init__(self, name):
        super(Filter, self).__init__(name)

    def set_filter_padding(self, in_data, out_data):
        """
        Should be overridden to define how wide the frame should be for each
        input data set
        """
        return {}

    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at
        a time

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
    def process(self, transport):
        """
        """
        in_data, out_data = self.get_datasets()
        self.set_filter_padding(in_data, out_data)
        transport.filter_chunk(self, in_data, out_data)
        # reset padding to none
        for data in in_data:
            data.padding = None

    def setup(self):
        self.exp.log(self.name + " Start")

        # Input datasets setup
        in_data, out_data = self.get_plugin_datasets()
        in_data[0].plugin_data_setup(pattern_name='PROJECTION',
                                     chunk=self.get_max_frames())

        # set details for all output data sets
        out_data[0].plugin_data_setup(pattern_name='PROJECTION',
                                      chunk=self.get_max_frames(),
                                      shape=in_data[0].data_obj.
                                      get_shape())

        # copy or add patterns related to this dataset
        out_data[0].data_obj.copy_patterns(in_data[0].data_obj.get_patterns())
        self.exp.log(self.name + " End")

    def organise_metadata(self):
        pass

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
