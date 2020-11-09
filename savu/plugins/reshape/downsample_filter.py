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
import numpy
import skimage.measure as skim

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class DownsampleFilter(Plugin, CpuPlugin):
    """
    A plugin to reduce the data in the selected dimension by a proportion

    :u*param bin_size: Bin Size for the downsample. Default: 2.
    :u*param mode: One of 'mean', 'median', 'min', 'max'. Default: 'mean'.
    :u*param pattern: One of 'PROJECTION' or 'SINOGRAM'. Default: 'PROJECTION'.
    """

    def __init__(self):
        logging.debug("Starting Downsample Filter")
        super(DownsampleFilter,
              self).__init__("DownsampleFilter")
        self.out_shape = None
        self.mode_dict = { 'mean'  : numpy.mean,
                           'median': numpy.median,
                           'min'   : numpy.min,
                           'max'   : numpy.max }

    def get_output_shape(self, input_data):
        input_shape = input_data.get_shape()
        core_dirs = input_data.get_core_directions()
        output_shape = []
        for i in range(len(input_shape)):
            if i in core_dirs:
                output_shape.append(input_shape[i]/self.parameters['bin_size'])
            else:
                output_shape.append(input_shape[i])

        return output_shape

    def process_frames(self, data):
        logging.debug("Running Downsample data")
        if self.parameters['mode'] in self.mode_dict:
            sampler = self.mode_dict[self.parameters['mode']]
        else:
            logging.warning("Unknown downsample mode. Using 'mean'.")
            sampler = numpy.mean
        block_size = (self.parameters['bin_size'], self.parameters['bin_size'])
        result = skim.block_reduce(data[0], block_size, sampler)
        return result

    def setup(self):
        # get all in and out datasets required by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # get plugin specific instances of these datasets
        in_pData, out_pData = self.get_plugin_datasets()

        plugin_pattern = self.parameters['pattern']
        in_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())

        self.out_shape = \
            self.new_shape(in_dataset[0].get_shape(), in_dataset[0])

        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=self.out_shape)

        out_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())

    def new_shape(self, full_shape, data):
        core_dirs = data.get_core_dimensions()
        new_shape = list(full_shape)
        for dim in core_dirs:
            new_shape[dim] = full_shape[dim] // self.parameters['bin_size']
            if (full_shape[dim] % self.parameters['bin_size']) > 0:
                new_shape[dim] += 1
        return tuple(new_shape)

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        # This filter processes one frame at a time
        return 'single'
