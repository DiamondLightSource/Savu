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
from savu.plugins.base_correction import BaseCorrection

import numpy as np

from savu.plugins.utils import register_plugin


@register_plugin
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
        image_key = self.get_in_datasets()[0].data
        self.dark = self.apply_preview(image_key.dark_mean())
        self.flat = self.apply_preview(image_key.flat_mean())
        self.flat_minus_dark = self.flat - self.dark
        self.nFrames = self.get_max_frames()
        self.slice_dim = self.get_plugin_in_datasets()[0].get_slice_dimension()
        data_shape = self.get_plugin_in_datasets()[0].get_shape()
        self.nDims = len(data_shape)
        self.tile = [1]*self.nDims
        self.tile[0] = data_shape[0]
        self.index = [slice(None), slice(None)]

    def correct(self, data):
        sl = self.slice_list[self.slice_dim]
        self.index[0] = slice(sl.start, sl.start + self.nFrames)
        dark = np.tile(self.dark[self.index], self.tile)
        flat_minus_dark = np.tile(self.flat_minus_dark[self.index], self.tile)

        data = (data-dark)/flat_minus_dark
        # finally clean up and trim the data
        data = np.nan_to_num(data)

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
