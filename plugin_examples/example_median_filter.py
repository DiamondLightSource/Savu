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
.. module:: example_median_filter
   :platform: Unix
   :synopsis: A plugin to filter each frame with a 3x3 median filter

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

import scipy.signal.signaltools as sig


class ExampleMedianFilter(BaseFilter, CpuPlugin):

    def __init__(self):
        logging.debug("Starting Median Filter")
        super(ExampleMedianFilter, self).__init__("ExampleMedianFilter")

    def filter_frames(self, data):
        result = sig.medfilt(data[0], self.parameters['kernel_size'])
        return result

    def set_filter_padding(self, in_data, out_data):
        padding = (self.parameters['kernel_size'][0]-1) // 2
        in_data[0].padding = {'pad_multi_frames': padding}
        out_data[0].padding = {'pad_multi_frames': padding}

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 8
