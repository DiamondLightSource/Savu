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
.. module:: timeseries_field_corrections
   :platform: Unix
   :synopsis: A Plugin to apply a simple dark and flatfield correction to some
       raw timeseries data

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

:synopsis: A Plugin to apply a simple dark and flatfield correction to some
       raw timeseries data

"""

from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.corrections.base_correction import BaseCorrection

import numpy as np

from savu.plugins.utils import register_plugin

#@register_plugin
class TimeseriesFieldCorrections(BaseCorrection, CpuPlugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data
    """

    def __init__(self):
        super(TimeseriesFieldCorrections,
              self).__init__("TimeseriesFieldCorrections")
        # TODO these should probably be parameters
        self.LOW_CROP_LEVEL = 0.0
        self.HIGH_CROP_LEVEL = 2.0
        self.WARN_PROPORTION = 0.05  # 5%
        self.flag_low_warning = False
        self.flag_high_warning = False

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        self.dark = inData.data.dark_mean()
        self.flat = inData.data.flat_mean()
        self.flat_minus_dark = self.flat - self.dark

        self.flat_minus_dark = self.flat - self.dark
        det_dims = [inData.get_data_dimension_by_axis_label('detector_y'),
                    inData.get_data_dimension_by_axis_label('detector_x')]

        self.convert_size = \
            lambda x, sl: x[[sl[d] for d in det_dims]]

    def process_frames(self, data):
        data = data[0]
        dark = self.convert_size(self.dark, self.get_current_slice_list()[0])
        flat_minus_dark = self.convert_size(
            self.flat_minus_dark, self.get_current_slice_list()[0])
        data = np.nan_to_num((data-dark)/flat_minus_dark)

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

        return data

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
