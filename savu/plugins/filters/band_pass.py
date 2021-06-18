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
.. module:: band_pass
   :platform: Unix
   :synopsis: A plugin to low pass each frame with a gaussian

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from scipy.ndimage.filters import gaussian_filter
from savu.plugins.utils import register_plugin


@register_plugin
class BandPass(BaseFilter, CpuPlugin):

    def __init__(self):
        """
        This is where the class is designed, and we inherit from 2 classes, the
        first is the Filter class, which deals with splitting the job up for
        us, and provides some simple methods which we need to overload. The
        second is the CpuPlugin class which tells the framework that the
        processing that you are doing here runs on 1 cpu.
        """
        logging.debug("initialising BandPass filter")
        logging.debug("Calling super to make sure that all superclases are " +
                      " initialised")
        super(BandPass,
              self).__init__("BandPass")

    def process_frames(self, data):
        """
        The second method we need to implement from the Filter class and the
        part of the code that actually does all the work. the input here 'data'
        will contain the 3D block of data to process, and we need to return the
        data for the single frame in the middle of this. In this case we use
        the scipy median filter with the 'kernel_size' parameter, and return
        the same size data as you had originally.
        """
        data = data[0]
        logging.debug("Data frame received for processing of shape %s",
                      str(data.shape))
        if self.parameters['type'] == 'Low':
            result = gaussian_filter(data, tuple(self.parameters['blur_width']))
        elif self.parameters['type'] == 'High':
            lp = gaussian_filter(data, tuple(self.parameters['blur_width']))
            result = data - lp
        return result
