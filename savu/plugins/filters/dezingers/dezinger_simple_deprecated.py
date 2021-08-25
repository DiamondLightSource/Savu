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
.. module:: dezinger_simple_deprecated
   :platform: Unix
   :synopsis: A plugin to remove zingers

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

import scipy.signal.signaltools as sig

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class DezingerSimpleDeprecated(BaseFilter, CpuPlugin):
    """
    """

    def __init__(self):
        super(DezingerSimpleDeprecated, self).__init__("DezingerSimpleDeprecated")
        self.zinger_proportion = 0.0
        self.frame_limit = 8

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        self.proj_dim = inData.data.proj_dim

        self._kernel = [1]*3
        self._kernel[self.proj_dim] = self.kernel_size

        pad_list = [(0, 0)]*3
        pad_list[self.proj_dim] = (self.pad, self.pad)

        dark = inData.data.dark()
        flat = inData.data.flat()
        if dark.size:
            dark = np.pad(inData.data.dark(), pad_list, mode='edge')
            dark = self._process_calibration_frames(dark)
            inData.data.update_dark(dark[self.pad:-self.pad])
        if flat.size:
            flat = np.pad(inData.data.flat(), pad_list, mode='edge')
            flat = self._process_calibration_frames(flat)
            inData.data.update_flat(flat[self.pad:-self.pad])

    def _process_calibration_frames(self, data):
        nSlices = data.shape[self.proj_dim] - 2*self.pad
        nSublists = int(np.ceil(nSlices/float(self.frame_limit)))
        idx = np.array_split(np.arange(self.pad, nSlices+self.pad), nSublists)
        idx = [np.arange(a[0]-self.pad, a[-1]+self.pad+1) for a in idx]
        out_sl = np.tile([slice(None)]*3, [len(idx), 1])
        out_sl[:, self.proj_dim] = idx
        result = np.empty_like(data)
        for sl in out_sl:
            result[tuple(sl)] = self._dezing(data[tuple(sl)])
        return result

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

    def process_frames(self, data):
        return self._dezing(data[0])

    def get_max_frames(self):
        """ Setting nFrames to multiple with an upper limit of 4 frames. """
        return ['multiple', self.frame_limit]

    def raw_data(self):
        return True

    def set_filter_padding(self, in_data, out_data):
        # kernel size must be odd
        ksize = self.parameters['kernel_size']
        self.kernel_size = ksize+1 if ksize % 2 == 0 else ksize

        in_data = in_data[0]
        self.pad = (self.kernel_size - 1) // 2
        self.data_size = in_data.get_shape()
        in_data.padding = {'pad_multi_frames': self.pad}
        out_data[0].padding = {'pad_multi_frames': self.pad}

    def executive_summary(self):
        if self.zinger_proportion > 0.5:
            return ["Over 50% of the pixels were treated as zingers!!"]
        if self.zinger_proportion > 0.05:
            return ["Over 5% of the pixels were treated as zingers"]
        return ["Nothing to Report"]
