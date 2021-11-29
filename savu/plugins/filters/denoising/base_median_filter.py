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
.. module:: base_median_filter
   :platform: Unix
   :synopsis: A base class for CPU/GPU median filter

.. moduleauthor::Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.core.iterate_plugin_group_utils import \
    setup_iterative_plugin_out_datasets

class BaseMedianFilter(Plugin, CpuPlugin):

    def __init__(self, name='BaseMedianFilter'):
        super(BaseMedianFilter, self).__init__(name)
        self.frame_limit = 1

    def setup(self):
        if self.exp.meta_data.get('is_end_plugin_in_iterate_group'):
            patterns = {
                'plugin_in_dataset': self.parameters['pattern'],
                'plugin_out_datasets': self.parameters['pattern']
            }
            in_dataset, out_dataset = self.get_datasets()
            in_pData, out_pData = self.get_plugin_datasets()
            setup_iterative_plugin_out_datasets(in_dataset, out_dataset,
                in_pData, out_pData, patterns, self.get_max_frames())
        else:
            # the plugin is not the end plugin in an iterative loop, so its
            # output datasets can be set normally
            in_dataset, out_dataset = self.get_datasets()
            out_dataset[0].create_dataset(in_dataset[0])
            in_pData, out_pData = self.get_plugin_datasets()
            in_pData[0].plugin_data_setup(self.parameters['pattern'],
                                          self.get_max_frames())
            out_pData[0].plugin_data_setup(self.parameters['pattern'],
                                           self.get_max_frames())

    def set_filter_padding(self, in_data, out_data):
        # kernel size must be odd
        ksize = self.parameters['kernel_size']
        self.kernel_size = ksize+1 if ksize % 2 == 0 else ksize

        if self.parameters['kernel_dimension'] == '3D':
            in_data = in_data[0]
            self.pad = (self.kernel_size - 1) // 2
            self.data_size = in_data.get_shape()
            in_data.padding = {'pad_multi_frames': self.pad}
            out_data[0].padding = {'pad_multi_frames': self.pad}

            if self.exp.meta_data.get('is_end_plugin_in_iterate_group'):
                # set the padding for the cloned dataset as well
                out_data[1].padding = {'pad_multi_frames': self.pad}

    def get_max_frames(self):
        """ Setting nFrames to multiple with an upper limit of 4 frames. """
        return ['multiple', self.frame_limit]

    # total number of output datasets
    def nOutput_datasets(self):
        if self.exp.meta_data.get('is_end_plugin_in_iterate_group'):
            return 2
        else:
            return 1

    # total number of output datasets that are clones
    def nClone_datasets(self):
        if self.exp.meta_data.get('is_end_plugin_in_iterate_group'):
            return 1
        else:
            return 0