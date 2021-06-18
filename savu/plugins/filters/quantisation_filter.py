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
.. module:: quantisation_filter
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
class QuantisationFilter(BaseFilter, CpuPlugin):

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
        super(QuantisationFilter,
              self).__init__("QuantisationFilter")
        self.level_list = None
        self.threshold_list = None
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
        result = data

        if self.highest is not None and self.lowest is not None:
            if self.highest < self.lowest:
                logging.error("Highest intensity < lowest intensity for some reason. Returning original data.")
            else:
                if len(self.level_list) < 1:
                    logging.error("Not enough quantisation levels to work with. Returning original data.")
                else:
                    result = numpy.zeros(data.shape, dtype=data.dtype)

                    if len(self.level_list) == 1:
                        logging.warning("Number of levels == 1. Result will be one colour only.")
                        result = self.level_list[0]
                    else:
                        if self.highest == self.lowest:
                            logging.warning("Highest intensity == lowest intensity. Result will be one colour only.")

                        result[ data < self.threshold_list[0] ] = self.level_list[0]
                        for i in range(1, len(self.threshold_list)):
                            lt = self.threshold_list[i - 1]
                            ht = self.threshold_list[i]
                            result[ numpy.logical_and(lt <= data, data < ht) ] = self.level_list[i]
                        result[ data >= self.threshold_list[-1] ] = self.level_list[-1]

        else:
            logging.error("No min/max intensities to work with. Returning original data.")

        return result

    def pre_process(self):
        in_dataset = self.get_in_datasets()[0]

        if self.parameters['explicit_min_max']:
            self.lowest = self.parameters['min_intensity']
            self.highest = self.parameters['max_intensity']

        else:
            try:
                # Extract the intensity range from the image meta data
                self.lowest = numpy.amin(in_dataset.meta_data.get('min'))
                self.highest = numpy.amax(in_dataset.meta_data.get('max'))

            except KeyError as k:
                logging.error("Caught KeyError in Quantisation.setup(): %s", str(k))

                # Use defaults suitable for tomo test data
                logging.warning("Using test data min and max intensities.")
                self.lowest = 0
                self.highest = 31137

        # Precompute the list of levels and thresholds from the intensity range
        self.level_list = numpy.linspace( self.lowest, self.highest, self.parameters['levels'] )
        self.threshold_list = numpy.linspace( self.lowest, self.highest, self.parameters['levels'] + 1 )[1:-1]
