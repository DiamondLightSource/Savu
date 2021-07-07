# Copyright 2018 Diamond Light Source Ltd.
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
.. module:: visual_hulls_recon
   :platform: Unix
   :synopsis: simple visual hulls reconstruction

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging
import numpy as np

from scipy.ndimage.filters import median_filter
from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class VisualHullsRecon(BaseRecon, CpuPlugin):

    def __init__(self):
        logging.debug("initialising Scikitimage Filter Back Projection")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(VisualHullsRecon,
              self).__init__("VisualHullsRecon")

    def _mapping_array(self, array_shape, center, theta):
        x, y = np.meshgrid(np.arange(-center, array_shape[0] - center),
                           np.arange(-center, array_shape[1] - center))
        return x*np.cos(theta) - y*np.sin(theta)

    def _recon_hull(self, sino, centre, angles):
        data_shape = (sino.shape[1], sino.shape[1])
        full = np.ones(data_shape)
        for i in range(len(angles)):
            mapping_array = self._mapping_array(data_shape, centre, np.deg2rad(angles[i]))
            mapping_array = np.clip(mapping_array.astype('int')+centre, 0,
                                    sino.shape[1]-1).astype('int')
            mask = sino[i, :][mapping_array]
            full -= 1-mask
        data_range = full.max() - full.min()
        full += data_range // 4
        full[full < 0.5] = 0
        return full

    def _binarize_sinogram(self, input_sinogram, threshold):
        sino = np.zeros_like(input_sinogram)
        sino[input_sinogram > threshold] = 1
        # as this is a simple routine, do a quick median filter to
        # get rid of any stray pixels in the binarization.
        sino = median_filter(sino, size=3)
        return sino

    def process_frames(self, data):
        sinogram = self._binarize_sinogram(data[0],
                                           self.parameters['threshold'])
        centre_of_rotations, angles, vol_shape, init = \
            self.get_frame_params()
        recon = self._recon_hull(sinogram, centre_of_rotations, angles)
        return recon

    def get_max_frames(self):
        return 'single'
