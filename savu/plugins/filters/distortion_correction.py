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

    :param polynomial_coeffs: Parameters of the radial distortion function. Default: (1, 0, 0, 0, 0).
    :param centre: Centre of distortion. Default: (1000, 1000)
    """

    def __init__(self):
        super(DistortionCorrection, self).__init__("DistortionCorrection")

    def pre_process(self):
        unwarp.setctr(*(self.parameters['centre']))
        #pass two empty arrays of frame chunk size
        unwarp.setcoeff(*self.parameters['polynomial_coeffs']) # need to unwrap the tuple
        unwarp.setctr(*self.parameters['centre'])
        unwarp.setup(data, result)

    def filter_frames(self, data):
        data = data[0]
        result = np.empty_like(data)
        # should the setup function be called here?
        unwarp.run(data, result)
        return result

    def post_process(self):
        # should this be called here?
        unwarp.cleanup()

    def setup(self):
        self.exp.log(self.name + " Start")
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # get only frames where image key is zero
        in_dataset[0].set_image_key(0)

        # copy all required information from in_dataset[0]
        out_dataset[0].create_dataset(in_dataset[0])

        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()
        # set pattern_name and nframes to process for all datasets
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())
        out_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())

        self.exp.log(self.name + " End")

    def get_max_frames(self):
        return 8
