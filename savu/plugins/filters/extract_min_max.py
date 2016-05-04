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
.. module:: extract_min_max
   :platform: Unix
   :synopsis: A plugin to extract the minimum and maximum intensity of a dataset

.. moduleauthor:: Nicoletta De Maio <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class ExtractMinMax(BaseFilter, CpuPlugin):
    """
    A plugin to extract the minimum and maximum intensity of a dataset
    """

    def __init__(self):
        """
        This is where the class is designed, and we inherit from 2 classes, the
        first is the Filter class, which deals with splitting the job up for
        us, and provides some simple methods which we need to overload. The
        second is the CpuPlugin class which tells the framework that the
        processing that you are doing here runs on 1 cpu.
        """
        logging.debug("initialising ExtractMinMax plugin")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(ExtractMinMax,
              self).__init__("ExtractMinMax")

        self.min = 0
        self.max = 0

    def filter_frames(self, data):
        """
        The second method we need to implement from the Filter class and the
        part of the code that actually does all the work. Unusually, the data
        here is returned unmodified because the current minimum and maximum
        intensities are buffered in the plugin itself.
        """
        data = data[0]
        logging.debug("Data frame recieved for processing of shape %s",
                      str(data.shape))

        mintmp = numpy.amin(data)
        maxtmp = numpy.amin(data)

        if mintmp < self.min:
            self.min = mintmp

        if maxtmp > self.max:
            self.max = maxtmp

        print "Current (min, max):", (self.min, self.max)

        return data

    def post_process(self):
        """
        Store the global minimum and maximum intensities as metadata.
        """
        out_dataset = self.get_out_datasets()[0]
        out_dataset.meta_data.set_meta_data(['min', 'max'], [self.min, self.max])