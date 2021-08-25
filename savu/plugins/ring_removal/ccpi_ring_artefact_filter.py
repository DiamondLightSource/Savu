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
.. module:: ccpi_ring_artefact_filter
   :platform: Unix
   :synopsis: Regularization-based method for removing ring artifacts.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from ccpi.reconstruction.parallelbeam import filters as ccpi_filters

from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.filters.base_filter import BaseFilter


@register_plugin
class CcpiRingArtefactFilter(BaseFilter, CpuPlugin):
    """
    This plugin applies the same ring removal method as the DLS tomo_recon\
    reconstruction software.

    :u*param param_r: The correction strength - decrease (typically in order \
    of magnitude steps) to increase ring supression, or increase to reduce \
    ring supression. Default: 0.005.

    :param param_n: Unknown description (for plate-like objects \
    only). Default: 0.
    :u*param num_series: High aspect ration compensation (for plate-like \
    objects only) . Default: 1.
    """

    def __init__(self):
        super(CcpiRingArtefactFilter, self).__init__(
                "CcpiRingArtefactFilter")

    def process_frames(self, data):
        param_n = self.parameters['param_n']
        param_r = self.parameters['param_r']
        num_series = self.parameters['num_series']

        return ccpi_filters.aml_ring_artefacts(
                data[0], param_n, param_r, num_series)

    def get_plugin_pattern(self):
        return 'SINOGRAM'
