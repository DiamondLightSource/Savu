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
from re import search

"""
.. module:: projection_vertical_alignment
   :platform: Unix
   :synopsis: Align each projection vertically with shift values calculated\
       using the ProjectionShift plugin

.. moduleauthor:: Mark Basham <mark.basham@rfi.ac.uk>

"""

import logging
import numpy as np
from scipy.ndimage.interpolation import shift as sci_shift

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

@register_plugin
class ProjectionShiftFromXComAndYProfile(BaseFilter, CpuPlugin):
    """
    Correct for vertical shift over projection images.

    :config_warn: Requires the PluginShift plugin to precede it.
    """

    def __init__(self):
        logging.debug("initialising Projection Alignment")
        super(ProjectionShiftFromXComAndYProfile, self).__init__(
            "ProjectionShiftFromXComAndYProfile")

    def _sinfunc(self, data, a, b, c):
        result = (a*np.sin(np.deg2rad(data-b)))+c
        return result

    def _profilefunc(self, data, a):
        result = sci_shift(self.match_profile, [a], mode='nearest')
        return result

    def _match_curves(self, curve1, curve2, search_extent):
        # filter the curves to remove some noise
        window = int(curve1.shape[0]/20)
        if(window%2==0):
            window += 1
        curve1 = savgol_filter(curve1, window, 3)
        curve2 = savgol_filter(curve2, window, 3)
        search_range = np.arange(-search_extent, search_extent)
        match_metric = np.zeros_like(search_range, dtype=np.float32)

        for i in range(search_range.shape[0]):
            compare = sci_shift(curve2, [search_range[i]], mode='nearest')
            match_metric[i] = np.sum(np.square((curve1-compare)[search_extent+1:-(search_extent+1)]))
        result = np.argmin(match_metric)
        return search_range[result]

    def pre_process(self):
        data = self.get_in_datasets()[0]
        # First sort out the x centre of mass calculation
        x_com = data.meta_data.get('x_com')
        rot_angle = data.meta_data.get('rotation_angle')

        fitpars, _ = curve_fit(self._sinfunc, rot_angle, x_com)
        fitted = self._sinfunc(rot_angle, *fitpars)
        residual = fitted - x_com

        self.centre_of_rotation = np.array([fitpars[2]])

        self.x_shifts = residual

        # Now work out the y shifts
        y_profile = data.meta_data.get('y_profile')

        # calculate the positive shifts through the system
        y_shifts_diff = np.zeros_like(x_com, dtype=np.int32)
        for i in range(0, y_profile.shape[0]-1):
            profile1 = y_profile[i, :]
            profile2 = y_profile[i+1, :]
            shift = self._match_curves(profile1, profile2, 100)
            y_shifts_diff[i+1] = shift

        y_shifts_diff[0] = int(np.mean(y_shifts_diff))

        self.y_shifts = np.cumsum(y_shifts_diff)

    def process_frames(self, data):
        data = data[0]

        in_plugin_data = self.get_plugin_in_datasets()[0]
        pos = in_plugin_data.get_current_frame_idx()[0]

        output = sci_shift(data,
                           [self.y_shifts[pos], int(self.x_shifts[pos])],
                           cval=np.nan)
        return output

    def get_max_frames(self):
        return 1

    def post_process(self):
        #in_meta_data = self.get_in_meta_data()[0]
        #in_meta_data.set('centre_of_rotation', self.centre_of_rotation)
        pass