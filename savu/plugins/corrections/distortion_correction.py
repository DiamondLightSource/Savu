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

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import unwarp


@register_plugin
class DistortionCorrection(BaseFilter, CpuPlugin):
    """
    A plugin to apply radial distortion correction.

    :param polynomial_coeffs: Parameters of the radial distortion \
    function. Default: (1.00015076, 1.9289e-6, -2.4325e-8, 1.00439e-11, -3.99352e-15).
    :param centre_y: The det_y coordinate of the centre of \
    distortion=(det_y, det_x) with origin (0, 0) in the top left \
    corner. Default: 995.24.
    :param centre_x: The det_x coordinate of the centre of \
    distortion=(det_y, det_x) with origin (0, 0) in the top left \
    corner. Default: 1283.25.
    :u*param crop_edges: When applied to previewed/cropped data, the result \
    may contain zeros around the edges, which can be removed by \
    cropping the edges by a specified number of pixels. Default: 0
    """

    def __init__(self):
        super(DistortionCorrection, self).__init__("DistortionCorrection")

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        shift = self.get_in_datasets()[0].data_info.get('starts')
        det_y = in_pData.get_data_dimension_by_axis_label('detector_y')
        det_x = in_pData.get_data_dimension_by_axis_label('detector_x')

        # If the data is cropped then the centre of distortion must be shifted
        # accordingly, e.g if preview is [:, a:b, c:d] then shift is (a, c)
        centre = np.array([self.parameters['centre_y'],
                           self.parameters['centre_x']])
        centre[0] -= shift[det_y]
        centre[1] -= shift[det_x]
        # flipping the values
        centre = centre[::-1]

        # pass two empty arrays of frame chunk size
        unwarp.setcoeff(*self.parameters['polynomial_coeffs'])
        unwarp.setctr(*centre)
        plugin_data_shape = in_pData.get_shape()
        temp_array = np.empty(plugin_data_shape, dtype=np.float32)
        unwarp.setup(temp_array, temp_array)

        self.new_slice = [slice(None)]*3
        orig_shape = self.get_in_datasets()[0].get_shape()
        for ddir in self.core_dims:
            self.new_slice[ddir] = \
                slice(self.crop, orig_shape[ddir]-self.crop)

    def process_frames(self, data):
        result = np.empty_like(data[0])
        unwarp.run(data[0], result)
        return result[self.new_slice]

    def post_process(self):
        unwarp.cleanup()

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())

        # copy all required information from in_dataset[0]
        self.shape = list(in_dataset[0].get_shape())
        self.core_dims = in_pData[0].meta_data.get('core_dims')
        self.crop = self.parameters['crop_edges']
        for ddir in self.core_dims:
            self.shape[ddir] = self.shape[ddir] - 2*self.crop
        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=tuple(self.shape))
        out_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())

    def get_max_frames(self):
        return 'multiple'
