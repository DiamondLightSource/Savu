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
.. module:: denoise using the split bregman method
   :platform: Unix
   :synopsis: A plugin to denoise 2D slices of data by using the Split Bregman
              to solve the Total Variation ROF model

.. moduleauthor:: Imanol Luengo <scientificsoftware@diamond.ac.uk>
"""
import logging

from skimage.restoration import denoise_tv_bregman

from savu.plugins.filter import Filter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class DenoiseBregmanFilter(Filter, CpuPlugin):
    """
    Split Bregman method for solving the denoising Total Variation ROF model.
    
    :param weight: Denoising factor. Default: 2.0
    :param max_iterations: Total number of iterations. Default: 100.
    :param error_threshold: Convergence threshold. Default: 0.001.
    :param isotropic: Isotropic or Anisotropic filtering. Default: False.
    """

    def __init__(self):
        logging.debug("Starting Denoise Bregman Filter")
        super(DenoiseBregmanFilter, self).__init__("DenoiseBregmanFilter")

    def get_filter_padding(self):
        return {}
    
    def get_max_frames(self):
        return 1

    def filter_frame(self, data):
        logging.debug("Running Denoise")
        weight = self.parameters['weight']
        max_iter = self.parameters['max_iterations']
        eps = self.parameters['error_threshold']
        isotropic = self.parameters['isotropic']
        return denoise_tv_bregman(data[0, ...], weight, max_iter=max_iter,
                                  eps=eps, isotropic=isotropic)