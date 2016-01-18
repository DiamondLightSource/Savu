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
.. moduleauthor:: Nicoletta De Maio <nicoletta.de-maio@diamond.ac.uk>

"""
import logging

from savu.plugins.filter import Filter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class DownsampleFilter(Filter, CpuPlugin):
    """
    A plugin to reduce the data in the selected direction by a proportion

    :param mode: Must be one of "skip", "median", "mean", "min" or "max". Default: "skip"
    :param bin_sizes: Bin Sizes for the downsample. Default: (1, 2, 2).
    """

    def __init__(self):
        logging.debug("Starting Downsample Filter")
        super(DownsampleFilter,
              self).__init__("DownsampleFilter")

    def get_output_shape(self, input_data):
        cropped = False
        result = ()
        input_shape = input_data.get_data_shape()
        if len(input_shape) != len(self.parameters['bin_sizes']):
            cropped = True
        for (dim, size) in zip(input_shape, self.parameters['bin_sizes']):
            result += (dim + 1) / size,
        return cropped, result

    def setup(self, experiment):
        logging.debug("Setting up Downsample data")
        #TODO: implement the rest...

    def filter_frame(self, data):
        logging.debug("Running Downsample data")
        # Sanity checking: fail for negative bin_sizes and fractional bin_sizes
        for size in self.parameters['bin_sizes']:
            intsize = int(size)
            if size < 1 or intsize != size:
                raise ValueError("DownsampleFilter: bin sizes must be positive integers, got %r"
                                 % self.parameters['bin_sizes'])
        # Check if result will be cropped
        cropped, shape = self.get_output_shape(data)
        # Report mismatched dimensions
        if cropped:
            self.report_string = self.report_string \
                               + "DownsampleFilter: Mismatch between data shape and number of bin sizes. " \
                               + "Data may have been cropped.\n"
        for (dim, size) in zip(shape, self.parameters['bin_sizes']):
            if dim < size:
                self.parameters['bin_sizes'] = dim
                self.report_string = self.report_string \
                                   + "DownsampleFilter: Bin size exceeds frame dimension. Bin size has been set to " \
                                   + str(dim) + " from " + str(size) + "\n"
        # Default filter (does nothing)
        filter_choice = self.null_filter
        # Choose downsampling function from mode...if it's on the list
        if self.parameters['mode'] in self.mode_dict:
            filter_choice = self.mode_dict[self.parameters['mode']]
        # Downsample the data
        result = self.filter_choice(data)
        return result

    def null_filter(self, data):
        self.report_string += "DownsampleFilter: Unknown mode %r. Returning data without changes\n" \
                            % self.parameters['mode']
        return data

    def skip_filter(self, data):
        return data[::self.parameters['bin_sizes'][0],
                    ::self.parameters['bin_sizes'][1],
                    ::self.parameters['bin_sizes'][2]]

    def median_filter(self, data):
        return data

    def mean_filter(self, data):
        return data

    def min_filter(self, data):
        return data

    def max_filter(self, data):
        return data

    mode_dict = {'skip':   skip_filter,
                 'median': median_filter,
                 'mean':   mean_filter,
                 'min':    min_filter,
                 'max':    max_filter}

    def report(self):
        return self.report_string
