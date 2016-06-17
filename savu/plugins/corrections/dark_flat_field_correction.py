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
.. module:: dark_flat_field_correction
   :platform: Unix
   :synopsis: A Plugin to apply a simple dark and flatfield correction to raw\
       timeseries data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.data.data_structures.data_type import ImageKey
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.base_correction import BaseCorrection
from savu.plugins.utils import register_plugin


@register_plugin
class DarkFlatFieldCorrection(BaseCorrection, CpuPlugin):
    """
    A Plugin to apply a simple dark and flat field correction to data.
    :param pattern: Data processing pattern is 'SINOGRAM' or \
        'PROJECTION'. Default: 'SINOGRAM'.
    """

    def __init__(self):
        super(DarkFlatFieldCorrection,
              self).__init__("DarkFlatFieldCorrection")
        # TODO these should probably be parameters
        self.LOW_CROP_LEVEL = 0.0
        self.HIGH_CROP_LEVEL = 2.0
        self.WARN_PROPORTION = 0.05  # 5%
        self.flag_low_warning = False
        self.flag_high_warning = False

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        if isinstance(inData.data, ImageKey):
            image_key = self.get_in_datasets()[0].data
            self.dark = image_key.dark_mean()
            self.flat = image_key.flat_mean()
        else:
            self.dark = inData.meta_data.get('dark')
            self.flat = inData.meta_data.get('flat')

        self.flat_minus_dark = self.flat - self.dark
        det_dims = [inData.find_axis_label_dimension('detector_y'),
                    inData.find_axis_label_dimension('detector_x')]

        data_shape = self.get_plugin_in_datasets()[0].get_shape()
        tile = [1]*len(data_shape)
        if self.parameters['pattern'] == 'PROJECTION':
            tile[0] = data_shape[0]
        self.convert_size = \
            lambda x, sl: np.tile(x[[sl[d] for d in det_dims]], tile)

    def correct(self, data):
        dark = self.convert_size(self.dark, self.slice_list)
        flat_minus_dark = \
            self.convert_size(self.flat_minus_dark, self.slice_list)
        data = np.nan_to_num((data-dark)/flat_minus_dark)
        self.__data_check(data)
        return data

    def __data_check(self, data):
        # make high and low crop masks
        low_crop = data < self.LOW_CROP_LEVEL
        high_crop = data > self.HIGH_CROP_LEVEL

        # flag if those masks include a large proportion of pixels, as this
        # may indicate a failure
        if ((float(low_crop.sum()) / low_crop.size) > self.WARN_PROPORTION):
            self.flag_low_warning = True
        if ((float(high_crop.sum()) / high_crop.size) > self.WARN_PROPORTION):
            self.flag_high_warning = True

        # Set all cropped values to the crop level
        data[low_crop] = self.LOW_CROP_LEVEL
        data[high_crop] = self.HIGH_CROP_LEVEL

    def executive_summary(self):
        summary = []
        if self.flag_high_warning:
            summary.append(("WARNING: over %i%% of pixels are being clipped as " +
                           "they have %f times the intensity of the provided flat field. "+
                           "Check your Dark and Flat correction images")
                           % (self.WARN_PROPORTION*100, self.HIGH_CROP_LEVEL))

        if self.flag_low_warning:
            summary.append(("WARNING: over %i%% of pixels are being clipped as " +
                           "they below the expected lower corrected threshold of  %f. " +
                           "Check your Dark and Flat correction images")
                           % (self.WARN_PROPORTION*100, self.LOW_CROP_LEVEL))

        if len(summary) > 0:
            return summary

        return ["Nothing to Report"]