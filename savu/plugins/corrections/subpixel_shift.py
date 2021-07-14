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
.. module:: subpixel_shift
   :platform: Unix
   :synopsis: A plugin to apply a subpixel x-shift to images
.. moduleauthor:: Malte Storm<malte.storm@diamond.ac.uk>
"""

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import scipy.ndimage.interpolation as sip
import numpy as np
import skimage.transform as sktf


@register_plugin
class SubpixelShift(BaseFilter, CpuPlugin):

    def __init__(self):
        super(SubpixelShift, self).__init__('SubpixelShift')

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        self.det_x = in_dataset[0]. \
            get_data_dimension_by_axis_label('detector_x')

        out_dataset[0].create_dataset(in_dataset[0])
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')
        if self.parameters['transform_module'] == 'skimage':
            self.process_frames = self.process_frames_skimage
        elif self.parameters['transform_module'] == 'scipy':
            self.process_frames = self.process_frames_scipy
        else:
            raise Exception('Transform module not supported.')

    def pre_process(self):
        self.xshift = float(self.parameters['x_shift'])
        if self.parameters['transform_module'] == 'skimage':
            self.xshift *= -1
            if self.xshift >= 0:
                self.pad_slice = slice(0, int(np.ceil(self.xshift)))
                self.pad_col = int(np.ceil(self.xshift))
            elif self.xshift < 0:
                self.pad_slice = slice(self.det_x + \
                                       int(np.floor(self.xshift)), self.det_x)
                self.pad_col = self.det_x + int(np.floor(self.xshift)) - 1
            self.tf = sktf.SimilarityTransform(scale=1, rotation=0, \
                                               translation=(self.xshift, 0))

    def process_frames_scipy(self, data):
        return sip.shift(data[0], (self.xshift, 0), mode='nearest', order=3)

    def process_frames_skimage(self, data):
        tmpdata = sktf.warp(data[0].astype(np.float64), self.tf) \
            .astype(np.float32)
        tmpdata[:, self.pad_slice] = tmpdata[:, self.pad_col][:, np.newaxis]
        return tmpdata

    def post_process(self):
        pass
