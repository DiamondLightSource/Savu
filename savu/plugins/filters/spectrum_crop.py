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
from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class SpectrumCrop(BaseFilter, CpuPlugin):
    """
    crops a spectrum to a range

    :param crop_range: range to crop to. Default: [2., 18.].

    """

    def __init__(self):
        logging.debug("cropping spectrum")
        super(SpectrumCrop, self).__init__("SpectrumCrop")

    def filter_frames(self, data):
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
        axis_labels = in_dataset[0].get_axis_label_keys()
        raw_axis = in_meta.get_meta_data(axis_labels[-1])
        print "the raw axis is"+str(raw_axis)
        self.new_idx = (raw_axis>crop_range[0]) & (raw_axis<crop_range[1])
        new_axis = raw_axis[self.new_idx]
        out_meta.set_meta_data(axis_labels[-1], new_axis)
        new_len = len(new_axis)
        print "newlen is"+str(new_len)
        shape = in_dataset[0].get_shape()[0:-1]+(new_len,)
        print shape
        cropped.set_shape(shape)
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1

    def nOutput_datasets(self):
        return 1
