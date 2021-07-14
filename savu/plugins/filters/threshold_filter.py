# Copyright 2016 Diamond Light Source Ltd.
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
.. module:: threshold_filter
   :platform: Unix
   :synopsis: A plugin to to quantise an image into a number of discrete levels

.. moduleauthor:: Nicoletta De Maio <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class ThresholdFilter(BaseFilter, CpuPlugin):

    def __init__(self):
        """
        This is where the class is designed, and we inherit from 2 classes, the
        first is the Filter class, which deals with splitting the job up for
        us, and provides some simple methods which we need to overload. The
        second is the CpuPlugin class which tells the framework that the
        processing that you are doing here runs on 1 cpu.
        """
        logging.debug("initialising Quantisation filter")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(ThresholdFilter,
              self).__init__("ThresholdFilter")
        self.threshold = None
        self.lowest = None
        self.highest = None

    def process_frames(self, data):
        """
        The second method we need to implement from the Filter class and the
        part of the code that actually does all the work. the input here 'data'
        will contain the 3D block of data to process, and we need to return the
        data for the single frame in the middle of this. In this case we return
        the same size data as you had originally.
        """
        data = data[0]
        logging.debug("Data frame recieved for processing of shape %s",
                      str(data.shape))

        result = numpy.zeros(data.shape, dtype=data.dtype)

        result[data < self.threshold] = self.lowest
        result[data >= self.threshold] = self.highest

        return result

    def pre_process(self):
        in_dataset = self.get_in_datasets()[0]
        try:
            # Extract the intensity range from the image meta data
            self.lowest = numpy.amin(in_dataset.meta_data.get('min'))
            self.highest = numpy.amax(in_dataset.meta_data.get('max'))
        except KeyError as k:
            logging.error("Caught KeyError in BinaryQuantisation.setup(): %s", str(k))

            # Use defaults suitable for tomo test data
            logging.warning("Using test data min and max intensities.")
            self.lowest = 0
            self.highest = 31137

        if self.parameters['explicit_threshold']:
            self.threshold = self.parameters['intensity_threshold']
        else:
            self.threshold = (self.highest + self.lowest) / 2.0
