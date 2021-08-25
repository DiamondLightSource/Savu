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
.. module:: time_based_plus_drift_correction
   :platform: Unix
   :synopsis: A time-based dark and flat field correction that accounts for\
       image drift (Note: A work in progress but please try).

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
from skimage.feature import match_template
from scipy.ndimage.interpolation import shift as sci_shift

from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.corrections.time_based_correction import TimeBasedCorrection
from savu.plugins.utils import register_plugin


@register_plugin
class TimeBasedPlusDriftCorrection(TimeBasedCorrection, CpuPlugin):

    def __init__(self):
        super(TimeBasedPlusDriftCorrection, self).__init__(
            "TimeBasedPlusDriftCorrection")

    def pre_process(self):
        super(TimeBasedPlusDriftCorrection, self).pre_process()

        self.shift_array = np.zeros((len(self.data_key), 2))
        # find shift between flat field frames
        self.template = self.flat[0][tuple(self.set_template_params())]
        self.drift = self.calculate_flat_field_drift(self.template)

    def set_template_params(self):
        template_params = []
        for p in self.parameters['template']:
            start, end = p.split(':')
            template_params.append(slice(int(start), int(end)))
        return template_params

    def calculate_flat_field_drift(self, template):
        drift = []
        for i in range(len(self.flat)-1):
            drift.append(self.calculate_shift(
                self.flat[i], self.flat[i+1], template))
        return drift

    def calculate_shift(self, im1, im2, template):
        index = []
        for im in [im1, im2]:
            match = match_template(im, template)
            index.append(np.unravel_index(np.argmax(match), match.shape))
        index = np.array(index)
        shift = index[1] - index[0]
        return shift

    def calculate_flat_field(self, frame, data, frames, distance):
        shift = self.calculate_shift(self.flat[frames[0]], data, self.template)
        flat1 = sci_shift(self.flat[frames[0]], tuple(shift), cval=np.nan)
        flat2 = sci_shift(self.flat[frames[1]], shift-self.drift[frames[0]],
                          cval=np.nan)
        flat1, flat2 = self.fill_nans(flat1, flat2)

        if frames[0] > 0:
            shift = shift + self.drift[frames[0]-1]
        self.shift_array[np.where(self.data_key == frame)[0]] = shift
        return flat1*distance[0] + flat2*distance[1]

    def fill_nans(self, im1, im2):
        im1[np.isnan(im1)] = im2[np.isnan(im1)]
        im2[np.isnan(im2)] = im1[np.isnan(im2)]
        return im1, im2

    def post_process(self):
        inData = self.get_in_datasets()[0]
        inData.meta_data.set('shift', self.shift_array)
