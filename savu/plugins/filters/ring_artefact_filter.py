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
.. module:: ring_artefact_filter
   :platform: Unix
   :synopsis: A plugin to perform ring artefact removal 

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import logging

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

import numpy as np

import ccpi_reconstruction

from savu.plugins.utils import register_plugin


class RingArtefactFilter(BaseFilter, CpuPlugin):
    """
    A plugin to perform ring artefact removal
    
    :param param_n: To be defined (param_n >= 1e-10). Default: 0.001.
    :param param_r: To be defined (param_r >= 1e-8). Default: 0.001.
    :param num_series: To be defined (1 <= num_series <= 100). Default: 20
    """

    def __init__(self):
        logging.debug("Starting ring artefact filter")
        super(RingArtefactFilter,
              self).__init__("RingArtefactFilter")


    def filter_frame(self, data):
        logging.debug("Running Filter data")
        
        param_n = self.parameters['param_n']
        param_r = self.parameters['param_r']
        num_series = self.parameters['num_series']
        
        self.param_check(param_n, param_r, num_series)         
        data = data.astype(np.float64)

        #ccpi_reconstruction.aml_ring_artefacts(data, param_n, param_r, num_series)
        
        return data


    def param_check(self, p1, p2, p3):
        if p1 < 1e-10:
            raise ValueError('param_n is too small')
            
        if p2 < 1e-8:
            raise ValueError('param_r is too small')
            
        if p3 < 1 or p3 > 100:
            raise ValueError('num_series is out of bounds')

