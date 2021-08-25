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
.. module:: find_peaks
   :platform: Unix
   :synopsis: A plugin to find the peaks

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
import peakutils as pe
import numpy as np
from scipy.signal import savgol_filter


@register_plugin
class FindPeaks(BaseFilter, CpuPlugin):

    def __init__(self):
        super(FindPeaks, self).__init__("FindPeaks")

    def process_frames(self, data):
        data = data[0]
        # filter to smooth noise
        data = savgol_filter(data, 51, 3)
        PeakIndex = pe.indexes(data, thres=self.parameters['thresh'],
                               min_dist=self.parameters['min_distance'])

        PeakIndexOut = np.zeros(data.shape)
        PeakIndexOut[PeakIndex] = 1
        return PeakIndexOut

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()

        # set pattern_name and nframes to process for all datasets
        in_pData[0].plugin_data_setup("SPECTRUM", self.get_max_frames())
        nFrames = in_pData[0].get_total_frames()
        labels = ['frames.index', 'position.idx']
        shape = (nFrames, in_dataset[0].get_shape()[-1])
        out_dataset[0].create_dataset(axis_labels=labels, shape=shape)
        out_dataset[0].add_pattern("CHANNEL", slice_dims=(1,), core_dims=(0,))
        out_dataset[0].add_pattern("SPECTRUM", slice_dims=(0,), core_dims=(1,))
        out_pData[0].plugin_data_setup("SPECTRUM", self.get_max_frames())

    def get_max_frames(self):
        return 'single'
