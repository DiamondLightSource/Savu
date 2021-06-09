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
.. module:: denoise_bregman_filter
   :platform: Unix
   :synopsis: A plugin to denoise 2D slices of data by using the Split Bregman \
              to solve the Total Variation ROF model

.. moduleauthor:: Imanol Luengo <scientificsoftware@diamond.ac.uk>
"""
import logging
import numpy as np

from skimage.restoration import denoise_tv_bregman

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class DenoiseBregmanFilter(BaseFilter, CpuPlugin):

    def __init__(self):
        logging.debug("Starting Denoise Bregman Filter")
        super(DenoiseBregmanFilter, self).__init__("DenoiseBregmanFilter")

    def get_filter_padding(self):
        return {}

    def process_frames(self, data):
        data = data[0]
        logging.debug("Running Denoise")
        weight = self.parameters['weight']
        max_iter = self.parameters['max_iterations']
        eps = self.parameters['error_threshold']
        isotropic = self.parameters['isotropic']
        data = np.nan_to_num(data[0, ...])
        result = denoise_tv_bregman(np.float64(data), weight, max_iter=max_iter,
                                    eps=eps, isotropic=isotropic)
        return result

    def get_max_frames(self):
        return 'multiple'
