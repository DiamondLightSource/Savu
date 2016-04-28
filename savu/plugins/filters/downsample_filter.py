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
import itertools

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

@register_plugin
class DownsampleFilter(BaseFilter, CpuPlugin):
    """
    A plugin to reduce the data in the selected direction by a proportion

    :param bin_size: Bin Size for the downsample. Default: 2.
    :param mode: One of 'skip', 'mean', 'median', 'min', 'max'. Default: 'mean'.
    :param pattern: One of 'PROJECTION' or 'SINOGRAM'. Default: 'PROJECTION'.
    """

    def __init__(self):
        logging.debug("Starting Downsample Filter")
        super(DownsampleFilter,
              self).__init__("DownsampleFilter")
        self.out_shape = None
        self.mode_dict = { 'skip'  : self.skip_sampler,
                           'mean'  : self.mean_sampler,
                           'median': self.median_sampler,
                           'min'   : self.min_sampler,
                           'max'   : self.max_sampler }

    def get_output_shape(self, input_data):
        input_shape = input_data.get_shape()
        return (input_shape[0],
                (input_shape[1]+1)/self.parameters['bin_size'],
                (input_shape[2]+1)/self.parameters['bin_size'])

    def filter_frames(self, data):
        logging.debug("Running Downsample data")
        if self.parameters['mode'] in self.mode_dict:
            sampler = self.mode_dict[self.parameters['mode']]
        else:
            logging.debug("Warning: unknown downsample mode. Using 'skip'.")
            sampler = self.skip_sampler
        result = sampler(data)
        return result

    def skip_sampler(self, data):
        logging.debug("Downsampling data using skip mode")
        new_slice = self.new_slice(data[0].shape)
        result = data[0][new_slice]
        return result

    def new_slice(self, data_shape):
        pData = self.get_plugin_in_datasets()[0]
        slice_dir = pData.get_slice_dimension()
        core_dirs = pData.get_core_directions()
        len_cores = len(core_dirs)
        len_data = len(data_shape)

        if len_cores is not len(data_shape):
            core_dirs = list(set(range(len_data)).difference(set([slice_dir])))

        new_slice = [slice(None)]*len(data_shape)
        for dim in range(len_cores):
            this_slice = slice(0, data_shape[dim], self.parameters['bin_size'])
            new_slice[dim] = this_slice
        return new_slice

    def mean_sampler(self, data):
        logging.debug("Downsampling data using mean mode")
        result = self.compress_bins(data, numpy.mean)
        return result

    def median_sampler(self, data):
        logging.debug("Downsampling data using median mode")
        result = self.compress_bins(data, numpy.median)
        return result

    def min_sampler(self, data):
        logging.debug("Downsampling data using median mode")
        result = self.compress_bins(data, numpy.amin)
        return result

    def max_sampler(self, data):
        logging.debug("Downsampling data using median mode")
        result = self.compress_bins(data, numpy.amax)
        return result

    def compress_bins(self, data, compressor):
        pData = self.get_plugin_in_datasets()[0]
        # Break up the input data
        blocks = self.get_blocks(data[0], pData.get_core_directions())
        # Downsampling step
        result = numpy.array(map(compressor, blocks))
        # Reshape the array (using Fortran-like ordering)
        slice_dir = pData.get_slice_dimension()
        result_shape = ()
        for s in range(0, len(self.out_shape)):
            if s != slice_dir:
                result_shape = result_shape + tuple([self.out_shape[s]])
        result = numpy.reshape(result, result_shape, order='F')
        return result

    def get_blocks(self, data, core_dirs):
        bin_size = self.parameters['bin_size']
        # Initialise the list of blocks
        blocks = [data]
        for dim in core_dirs:
            # Initialise the temporary block list
            stripes = []
            # Calculate the list of bin indices along dim
            nbins = self.out_shape[dim]
            bins = bin_size * numpy.arange(1, nbins)
            # Handle the fact that we're dealing with a 2d slice instead of a 3d lump
            if dim == 0:
                axis = dim
            else:
                axis = dim - 1
            # Subdivide all current blocks
            for block in blocks:
                tmp = numpy.array_split(block, bins, axis=axis)
                for t in tmp:
                    stripes.append(t)
            # Replace the list of blocks for the next iteration
            blocks = stripes
        return blocks

    def setup(self):
        # get all in and out datasets required by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # get plugin specific instances of these datasets
        in_pData, out_pData = self.get_plugin_datasets()

        plugin_pattern = self.parameters['pattern']
        in_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())

        self.out_shape = self.new_shape(in_dataset[0].get_shape(), in_pData[0])

        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=self.out_shape)

        out_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())

    def new_shape(self, full_shape, pData):
        core_dirs = pData.get_core_directions()
        new_shape = list(full_shape)
        for dim in core_dirs:
            new_shape[dim] = full_shape[dim]/self.parameters['bin_size'] \
                + full_shape[dim] % self.parameters['bin_size']
        return tuple(new_shape)

    def get_max_frames(self):
        return 1
