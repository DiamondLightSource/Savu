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
.. module:: downsample_filter
   :platform: Unix
   :synopsis: A plugin to filter each frame with a downsample

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class DownsampleFilter(BaseFilter, CpuPlugin):
    """
    A plugin to reduce the data in the selected direction by a proportion

    :param bin_size: Bin Size for the downsample. Default: 2.
    """

    def __init__(self):
        logging.debug("Starting Downsample Filter")
        super(DownsampleFilter,
              self).__init__("DownsampleFilter")

    def get_output_shape(self, input_data):
        input_shape = input_data.get_shape()
        return (input_shape[0],
                (input_shape[1]+1)/self.parameters['bin_size'],
                (input_shape[2]+1)/self.parameters['bin_size'])

    def filter_frames(self, data):
        logging.debug("Running Downsample data")
        new_slice = self.new_slice(data[0].shape)
        result = data[0][new_slice]
        return result

    def new_slice(self, data_shape):
        pData = self.get_plugin_in_datasets()[0]
        core_dirs = pData.get_core_directions()
        slice_dirs = pData.get_core_directions()
        new_slice = [slice(None)]*len(data_shape)
        for dim in core_dirs:
            this_slice = slice(0, data_shape[dim], self.parameters['bin_size'])
            new_slice[dim] = this_slice
        return new_slice

    def setup(self):
        # get all in and out datasets required by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # get plugin specific instances of these datasets
        in_pData, out_pData = self.get_plugin_datasets()

        plugin_pattern = self.get_plugin_pattern()
        in_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())

        new_shape = self.new_shape(in_dataset[0].get_shape(), in_pData[0])

        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=new_shape)

        out_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())

    def new_shape(self, full_shape, pData):
        core_dirs = pData.get_core_directions()
        new_shape = list(full_shape)
        for dim in core_dirs:
            new_shape[dim] = full_shape[dim]/self.parameters['bin_size'] \
                + full_shape[dim] % self.parameters['bin_size']
        return tuple(new_shape)
