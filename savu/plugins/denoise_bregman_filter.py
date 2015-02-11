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
.. module:: denoise using the bregman method
   :platform: Unix
   :synopsis: A plugin to filter each frame with a 3x3 median filter

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging

import numpy as np

import skimage.filter

from savu.plugins.filter import Filter
from savu.plugins.cpu_plugin import CpuPlugin


class DenoiseBregmanFilter(Filter, CpuPlugin):
    """
    Split Bregman method for solving the denoising Total Variation ROF model.
    
    :param weight: Denoising factor. Default: 2.
    :param max_iterations: Total number of iterations. Default: 100.
    :param error_threshold: Convergence threshold. Default: 0.001.
    :param isotropic: Isotropic or Anisotropic filtering. Default: False.
    """

    def __init__(self):
        logging.debug("Starting Denoise Bregman Filter")
        super(DenoiseBregmanFilter,
              self).__init__("DenoiseBregmanFilter")

    def populate_default_parameters(self):
        super(DenoiseBregmanFilter,
              self).populate_default_parameters()
        self.parameters['weight'] = 2
        self.parameters['max_iterations'] = 100
        self.parameters['error_threshold'] = 0.001
        self.parameters['isotropic'] = False

    def get_filter_padding(self):
        return {}

    def filter_frame(self, data):
        logging.debug("Running Denoise")
        result = []
        for i in range(data.shape[0]):
            result.append(skimage.filter.denoise_tv_bregman(data[i, :, :],
                                                            self.parameters['weight'],
                                                            max_iter=self.parameters['max_iterations'],
                                                            eps=self.parameters['error_threshold'],
                                                            isotropic=self.parameters['isotropic']))
        return np.transpose(np.dstack(result), (2, 0, 1))
