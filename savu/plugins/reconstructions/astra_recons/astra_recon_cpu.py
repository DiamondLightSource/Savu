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
.. module:: astra_recon_cpu
   :platform: Unix
   :synopsis: Wrapper around the Astra toolbox for cpu reconstruction
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.reconstructions.base_astra_recon import BaseAstraRecon
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.data.plugin_list import CitationInformation
from savu.plugins.utils import register_plugin


@register_plugin
class AstraReconCpu(BaseAstraRecon, CpuPlugin):
    """
    A Plugin to run the astra reconstruction

    :param number_of_iterations: Number of Iterations if an iterative method\
        is used . Default: 1.
    :param reconstruction_type: Reconstruction type \
        (FBP|SIRT|SART|ART|CGLS|FP|BP|). Default: 'FBP'.
    :param projector: Set astra projector (line|strip|linear). Default: 'line'.
    """

    def __init__(self):
        super(AstraReconCpu, self).__init__("AstraReconCpu")

    def get_parameters(self):
        return [self.parameters['reconstruction_type'],
                self.parameters['number_of_iterations']]

    def astra_setup(self):
        options_list = ["FBP", "SIRT", "SART", "ART", "CGLS", "FP", "BP"]
        if not options_list.count(self.parameters['reconstruction_type']):
            raise Exception("Unknown Astra CPU algorithm.")

    def set_options(self, cfg):
        return cfg
