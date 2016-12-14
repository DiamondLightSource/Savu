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
# $Id: dezing_filter.py 467 2016-02-16 11:40:42Z kny48981 $


"""
.. module:: dezing_filter
   :platform: Unix
   :synopsis: A plugin to remove dezingers

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

import scipy.signal.signaltools as sig

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class DezingFilter(BaseFilter, CpuPlugin):
    """
    A plugin for cleaning x-ray strikes based on statistical evaluation of \
    the near neighbourhood
    :param outlier_mu: Threshold for detecting outliers, greater is less \
    sensitive. Default: 1000.0.
    :param kernel_size: Number of frames included in average. Default: 5.
    """

    def __init__(self):
        super(DezingFilter, self).__init__("DezingFilter")
        self.zinger_proportion = 0.0

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        dark = inData.data.dark()
        flat = inData.data.flat()

        pad_list = ((self.pad, self.pad), (0, 0), (0, 0))

        self._kernel = (self.parameters['kernel_size'], 1, 1)

        dark = self._dezing(np.pad(dark, pad_list, mode='edge'))
        flat = self._dezing(np.pad(flat, pad_list, mode='edge'))
        inData.data.update_dark(dark[self.pad:-self.pad])
        inData.data.update_flat(flat[self.pad:-self.pad])

    def _dezing(self, data):
        result = data[...]
        median_result = sig.medfilt(data, self._kernel)
        differrence = np.abs(data-median_result)
        replace_mask = differrence > self.parameters['outlier_mu']
        self.zinger_proportion = \
            max(self.zinger_proportion, np.sum(replace_mask)/(
                np.size(replace_mask)*1.0))
        result[replace_mask] = median_result[replace_mask]
        return result

    def filter_frames(self, data):
        return self._dezing(data[0])

    def get_max_frames(self):
        """
        :returns:  an integer of the number of frames. Default 100
        """
        return 16

    def raw_data(self):
        return True

    def set_filter_padding(self, in_data, out_data):
        in_data = in_data[0]
        self.pad = (self.parameters['kernel_size'] - 1) / 2
        self.data_size = in_data.get_shape()
        in_data.padding = {'pad_multi_frames': self.pad}
        out_data[0].padding = {'pad_multi_frames': self.pad}

    def executive_summary(self):
        if self.zinger_proportion > 0.5:
            return ["Over 50% of the pixels were treated as zingers!!"]
        if self.zinger_proportion > 0.05:
            return ["Over 5% of the pixels were treated as zingers"]
        return ["Nothing to Report"]
