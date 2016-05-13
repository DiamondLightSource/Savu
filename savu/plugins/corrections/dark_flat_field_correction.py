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
.. module:: dark_flat_field_correction
   :platform: Unix
   :synopsis: A Plugin to apply a simple dark and flatfield correction to raw\
       timeseries data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.data.data_structures.data_type import ImageKey
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.base_correction import BaseCorrection
from savu.plugins.utils import register_plugin


@register_plugin
class DarkFlatFieldCorrection(BaseCorrection, CpuPlugin):
    """
    A Plugin to apply a simple dark and flat field correction to data.
    :param pattern: Data processing pattern is 'SINOGRAM' or \
        'PROJECTION'. Default: 'SINOGRAM'.
    """

    def __init__(self):
        super(DarkFlatFieldCorrection,
              self).__init__("DarkFlatFieldCorrection")

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        if isinstance(inData.data, ImageKey):
            image_key = self.get_in_datasets()[0].data
            self.dark = image_key.dark_mean()
            self.flat = image_key.flat_mean()
        else:
            self.dark = inData.meta_data.get_meta_data['dark']
            self.flat = inData.meta_data.get_meta_data['flat']

        self.flat_minus_dark = self.flat - self.dark
        self.nFrames = self.get_max_frames()
        self.slice_dim = self.get_plugin_in_datasets()[0].get_slice_dimension()
        data_shape = self.get_plugin_in_datasets()[0].get_shape()
        self.nDims = len(data_shape)
        self.tile = [1]*self.nDims
        if self.parameters['pattern'] is 'PROJECTION':
            self.tile[0] = data_shape[0]
        self.index = [slice(None), slice(None)]

    def correct(self, data):
        if self.parameters['pattern'] == 'SINOGRAM':
            sl = self.slice_list[self.slice_dim]
            self.index[0] = slice(sl.start, sl.start + self.nFrames)

        dark = np.tile(self.dark[self.index], self.tile)
        flat_minus_dark = np.tile(self.flat_minus_dark[self.index], self.tile)
        data = (data-dark)/flat_minus_dark
        # finally clean up and trim the data
        return np.nan_to_num(data)
