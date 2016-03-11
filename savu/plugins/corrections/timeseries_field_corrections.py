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
        self.LOW_CROP_LEVEL = 0
        self.HIGH_CROP_LEVEL = 2
        self.WARN_PROPORTION = 0.1  # 10%
        self.flag_low_warning = False
        self.flag_high_warning = False

    def pre_process(self):
        in_meta_data, out_meta_data = self.get_meta_data()
        image_keys = in_meta_data[0].get_meta_data('image_key')
        self.data_idx = np.where(image_keys == 0)[0]
        self.flat_idx = np.where(image_keys == 1)[0]
        self.dark_idx = np.where(image_keys == 2)[0]

    def correct(self, data):
        trimmed_data = data[self.data_idx]
        dark = data[self.dark_idx].mean(0)
        dark = np.tile(dark, (trimmed_data.shape[0], 1, 1))
        flat = data[self.flat_idx].mean(0)
        flat = np.tile(flat, (trimmed_data.shape[0], 1, 1))
        data = (trimmed_data-dark)/(flat-dark)

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
            self.flag_low_warning = True

        # Set all cropped values to the crop level
        data[low_crop] = self.LOW_CROP_LEVEL
        data[high_crop] = self.HIGH_CROP_LEVEL

        return data

    def executive_summary(self):
        if self.flag_high_warning or self.flag_low_warning:
            return ("WARNING: over 10% of pixels are being clipped, " +
                    "check your Dark and Flat field images are correct")
        return "Nothing to Report"
