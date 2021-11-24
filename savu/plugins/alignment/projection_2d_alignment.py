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
.. module:: projection_2d_alignment
   :platform: Unix
   :synopsis: calculates horizontal-vertical shift vectors for fixing misaligned projection data

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from skimage.registration import phase_cross_correlation

import numpy as np

@register_plugin
class Projection2dAlignment(Plugin, CpuPlugin):
    def __init__(self):
        super(Projection2dAlignment, self).__init__('Projection2dAlignment')

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())
        in_pData[1].plugin_data_setup('PROJECTION', self.get_max_frames())

        # create a metadata for storing shift vectors
        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        new_shape = (in_dataset[0].get_shape()[slice_dirs[0]], 2)
        out_dataset[0].create_dataset(shape=new_shape,
                                      axis_labels=['x.shifts', 'y.shifts'],
                                      remove=True)
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())

    def process_frames(self, data):
        projection = data[0]  # extract a projection
        projection_align = data[1]  # extract a projection for alignment

        shift, error, diffphase = phase_cross_correlation(
                    projection, projection_align, upsample_factor=self.parameters['upsample_factor'])
        return shift

    def post_process(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()

        out_data = self.get_out_datasets()[0]
        shift_vector = out_data.data[:, :]  # get a shift vector
        in_meta_data = self.get_in_meta_data()[0]
        in_meta_data.set('projection_shifts', shift_vector)
        self.exp.meta_data.set('projection_shifts', shift_vector)
        #self.exp.index[in_dataset[0]].meta_data.set('projection_shifts', shift_vector)
        #self.exp.index[in_dataset[0]].meta_data.set('projection_shifts', shift_vector)
        #for name in in_dataset:
        #    self.exp.index['in_data'][name].meta_data.set('projection_shifts', shift_vector)

        #for name in datasets:
        #    self.exp.index['in_data'][name].meta_data.set(key, value)
        #self.get_in_datasets()[0].meta_data.set('projection_shifts', out_data.data[:, :])
        #out_dataset[0].meta_data.set('rotation_angle', angles_meta_deg)

    def get_max_frames(self):
        return 'single'

    def nInput_datasets(self):
        return 2

    def nOutput_datasets(self):
        return 1
