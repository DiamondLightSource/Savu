# Copyright 2020 Diamond Light Source Ltd.
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
.. module:: dezinger
   :platform: Unix
   :synopsis: A 3D median-based dezinger plugin to apply to raw projection data
.. moduleauthor::Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from larix.methods.misc import MEDIAN_DEZING

@register_plugin
class Dezinger(BaseFilter, CpuPlugin):

    def __init__(self):
        super(Dezinger, self).__init__("Dezinger")
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
        indices = np.where(np.isnan(result))
        result[indices] = 0.0
        std_dev = np.std(result)
        result = MEDIAN_DEZING(result.copy(order='C'), self.parameters['kernel_size'], std_dev*self.parameters['outlier_mu'])
        return result

    def process_frames(self, data):
        input_temp = data[0]
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0
        std_dev = np.std(input_temp)
        result = MEDIAN_DEZING(input_temp.copy(order='C'), self.parameters['kernel_size'], std_dev*self.parameters['outlier_mu'])
        return result

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
