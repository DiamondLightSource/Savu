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
.. module:: scikitimage_sart
   :platform: Unix
   :synopsis: Wrapper for scikitimage SART function

"""

import logging
from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.plugins.driver.cpu_plugin import CpuPlugin

import skimage.transform as transform
import numpy as np
from scipy import ndimage

from savu.plugins.utils import register_plugin


@register_plugin
class ScikitimageSart(BaseRecon, CpuPlugin):

    def __init__(self):
        logging.debug("initialising Scikitimage SART")
        logging.debug("Calling super to make sure that all superclasses are " +
                      " initialised")
        super(ScikitimageSart, self).__init__("ScikitimageSart")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0] // 2) - float(centre_of_rotation)
        return ndimage.interpolation.shift(sinogram, centre_of_rotation_shift)

    def process_frames(self, data):
        sino = data[0]
        centre_of_rotations, angles, vol_shape, init = self.get_frame_params()
        in_pData = self.get_plugin_in_datasets()[0]
        sinogram = np.swapaxes(sino, 0, 1)
        sinogram = self._shift(sinogram, centre_of_rotations)
        sino = sinogram.astype(np.float64)
        theta = np.linspace(0, 180, sinogram.shape[1])
        result = \
            transform.iradon(sino, theta=theta,
                             output_size=(in_pData.get_shape()[1]),
                             # self.parameters['output_size'],
                             filter_name='ramp',  # self.parameters['filter'],
                             interpolation='linear',
                             # self.parameters['linear'],
                             circle=False)  # self.parameters[False])

        for i in range(self.parameters["iterations"]):
            print("Iteration %i" % i)
            result = transform.iradon_sart(sino, theta=theta, image=result,
                                           # self.parameters['result'],
                                           projection_shifts=None,
                                           # self.parameters['None'],
                                           clip=None,
                                           # self.parameters[None],
                                           relaxation=0.15
                                           # self.parameters[0.15])
                                           )
        return result

    def get_max_frames(self):
        return 'single'

