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
.. module:: projection_shift
   :platform: Unix
   :synopsis: Calculate horizontal and vertical shifts in the projection\
       images over time, using template matching.

.. moduleauthor:: Mark Basham <mark.basham@rfi.ac.uk>

"""

import logging
import numpy as np
from skimage.feature import match_template, match_descriptors, ORB
from scipy.linalg import lstsq
from skimage.transform import AffineTransform
from skimage.measure import ransac

from scipy.ndimage.measurements import center_of_mass

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class CalculateXComAndYProfile(BaseFilter, CpuPlugin):
    """
    Simply calculates the x centre of mass and the 
    Y profile for use in simplistic alignment processes

    :param out_datasets: Set the output dataset name. Default: ['x_com', 'y_profile'].
    """

    def __init__(self):
        logging.debug("initialising pre alignment calculations in CalculateXComAndYProfile")
        super(CalculateXComAndYProfile, self).__init__("CalculateXComAndYProfile")

    def process_frames(self, data):
        frame = data[0]
        y_profile = np.sum(frame, axis=1)

        # flip the fram as we want the dark areas to be more massive for this caluculation
        frame = np.abs(frame-np.max(frame))
        # trim out the low values to emphasise the bigger pieces # may not be good!
        frame[frame<frame.mean()] = 0
        frame[frame<frame.mean()] = 0
        
        x, y = center_of_mass(frame)

        return [np.array([x]), y_profile]

    def get_max_frames(self):
        return 1

    def nOutput_datasets(self):
        return 2

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())

        # Output dataset one is the x com
        new_shape = (in_dataset[0].get_shape()[0],1)

        out_dataset[0].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'])
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())

        # Output dataset 2 is the y profiles
        new_shape = (in_dataset[0].get_shape()[0],in_dataset[0].get_shape()[2])

        out_dataset[1].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'])
        out_dataset[1].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[1].plugin_data_setup('METADATA', self.get_max_frames())
