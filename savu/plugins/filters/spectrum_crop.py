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
.. module:: spectrum_crop
   :platform: Unix
   :synopsis: A plugin to crop a spectra

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""
import logging
import numpy as np
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class SpectrumCrop(BaseFilter, CpuPlugin):

    def __init__(self):
        logging.debug("cropping spectrum")
        super(SpectrumCrop, self).__init__("SpectrumCrop")

    def process_frames(self, data):
        data = data[0]
        data_cropped = data[self.new_idx]
        return data_cropped

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        cropped = out_datasets[0]
        cropped.create_dataset(in_dataset[0])
        in_meta = in_dataset[0].meta_data
        out_meta = cropped.meta_data
        crop_range = self.parameters['crop_range']
#         axis_labels = in_dataset[0].get_axis_label_keys()
        raw_axis = in_meta.get(self.parameters['axis'])
        logging.debug("the raw axis is: %s" % str(raw_axis))
        self.new_idx = (raw_axis>crop_range[0]) & (raw_axis<crop_range[1])
        new_axis = raw_axis[self.new_idx]
        out_meta.set(self.parameters['axis'], new_axis)
        new_len = len(new_axis)
#         print "newlen is"+str(new_len)
        shape = in_dataset[0].get_shape()[0:-1]+(new_len,)
#         print shape
        cropped.set_shape(shape)
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        return 'single'

    def nOutput_datasets(self):
        return 1
