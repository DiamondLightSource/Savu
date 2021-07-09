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
.. module:: scikitimage_filter_back_projection
   :platform: Unix
   :synopsis: Wrapper for scikitimage FBP function

"""

import logging
from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.plugins.driver.cpu_plugin import CpuPlugin

import skimage.transform as transform
import numpy as np
from scipy import ndimage

from savu.plugins.utils import register_plugin


@register_plugin
class ScikitimageFilterBackProjection(BaseRecon, CpuPlugin):

    def __init__(self):
        logging.debug("initialising Scikitimage Filter Back Projection")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(ScikitimageFilterBackProjection,
              self).__init__("ScikitimageFilterBackProjection")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0] // 2) - centre_of_rotation
        result = ndimage.interpolation.shift(sinogram,
                                             (centre_of_rotation_shift, 0))
        return result

    def process_frames(self, data):
        sino = data[0]
        centre_of_rotations, angles, vol_shape, init = self.get_frame_params()
        in_pData = self.get_plugin_in_datasets()[0]
        sinogram = np.swapaxes(sino, 0, 1)
        sinogram = self._shift(sinogram, centre_of_rotations)

        dim_detX = in_pData.get_data_dimension_by_axis_label('detector_x')
        size = self.parameters['output_size']
        size = in_pData.get_shape()[dim_detX] if size == 'auto' or \
            size is None else size

        result = \
            transform.iradon(sinogram, theta=angles,
                             output_size=(size),
                             filter_name=self.parameters['filter'],
                             interpolation=self.parameters['interpolation'],
                             circle=self.parameters['circle'])
        return result

    def get_max_frames(self):
        return 'single'
