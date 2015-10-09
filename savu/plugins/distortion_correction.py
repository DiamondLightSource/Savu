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
.. module:: distortion_correction
   :platform: Unix
   :synopsis: A plugin to apply a distortion correction

.. moduleauthor:: Nicola Wadeson<scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import unwarp


@register_plugin
class DistortionCorrection(BaseFilter, CpuPlugin):
    """
    A plugin to apply distortion correction

    :param centre: First param information. Default: (1000,1000).
    """

    def __init__(self):
        super(DistortionCorrection, self).__init__("DistortionCorrection")

    def pre_process(self):
        unwarp.setctr(*(self.parameters['centre']))

    def filter_frames(self, data):
        result = np.empty_like(data[0])
        print "running setup***"
        unwarp.setup(data[0], result)
        print "running run***"
        unwarp.run(data[0], result)
        return result

    def post_process(self, data):
        unwarp.cleanup()

    def get_max_frames(self):
        return 3
