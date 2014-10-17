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
.. module:: median_3x3_filter
   :platform: Unix
   :synopsis: A plugin to filter each frame with a 3x3 median filter

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.filter import Filter
from savu.plugins.cpu_plugin import CpuPlugin

import scipy.signal.signaltools as sig


class MedianFilter(Filter, CpuPlugin):
    """
    A plugin to filter each frame with a 3x3 median filter
    """

    def __init__(self):
        super(MedianFilter,
              self).__init__("MedianFilter")

    def populate_default_parameters(self):
        self.parameters['kernel_size'] = (1, 3, 3)

    def get_filter_width(self):
        width = (self.parameters['kernel_size'][0]-1)/2
        return width

    def filter_frame(self, data):
        result = sig.medfilt(data, self.parameters['kernel_size'])
        return result[result.shape[0]/2, :, :]
