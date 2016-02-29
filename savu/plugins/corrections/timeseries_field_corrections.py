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
        # does this line need to be done to all projections?
        data = np.nan_to_num(data)
        data[data < 0] = 0
        data[data > 2] = 2

        return data
