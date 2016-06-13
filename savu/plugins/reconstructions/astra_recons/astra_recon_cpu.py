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

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.description = \
            ("The reconstruction used to create this output is described in " +
             "this publication")
        cite_info.bibtex = \
            ("@article{palenstijn2011performance,\n" +
             "title={Performance improvements for iterative electron " +
             "tomography reconstruction using graphics processing units " +
             "(GPUs)},\n" +
             "author={Palenstijn, WJ and Batenburg, KJ and Sijbers, J},\n" +
             "journal={Journal of structural biology},\n" +
             "volume={176},\n" +
             "number={2},\n" +
             "pages={250--253},\n" +
             "year={2011},\n" +
             "publisher={Elsevier}\n" +
             "}")
        cite_info.endnote = \
            ("%0 Journal Article\n" +
             "%T Performance improvements for iterative electron tomography " +
             "reconstruction using graphics processing units (GPUs)\n" +
             "%A Palenstijn, WJ\n" +
             "%A Batenburg, KJ\n" +
             "%A Sijbers, J\n" +
             "%J Journal of structural biology\n" +
             "%V 176\n" +
             "%N 2\n" +
             "%P 250-253\n" +
             "%@ 1047-8477\n" +
             "%D 2011\n" +
             "%I Elsevier")
        cite_info.doi = "http://dx.doi.org/10.1016/j.jsb.2011.07.017"
        return cite_info
