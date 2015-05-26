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

from savu.plugins.filter import Filter
from savu.plugins.cpu_plugin import CpuPlugin

import ccpi

from savu.plugins.utils import register_plugin


@register_plugin
class RingArtefactFilter(Filter, CpuPlugin):
    """
    A plugin to perform ring artefact removal
    
    """

    def __init__(self):
        logging.debug("Starting ring artefact Filter")
        super(RingArtefactFilter,
              self).__init__("RingArtefactFilter")


    def filter_frame(self, data):
        logging.debug("Running Filter data")
        result = ccpi.aml_ring_artefacts(data, param_n, param_r, num_series)
        return result
