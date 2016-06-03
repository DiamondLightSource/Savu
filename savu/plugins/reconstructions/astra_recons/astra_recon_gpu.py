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
.. module:: astra_recon_gpu
   :platform: Unix
   :synopsis: Wrapper around the Astra toolbox for gpu reconstruction
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.reconstructions.new_base_astra_recon import NewBaseAstraRecon
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.data.plugin_list import CitationInformation
from savu.plugins.utils import register_plugin


@register_plugin
class AstraReconGpu(NewBaseAstraRecon, GpuPlugin):
    """
    A Plugin to run the astra reconstruction

    :param number_of_iterations: Number of Iterations if an iterative method\
        is used . Default: 1.
    :param res_norm: Output the residual norm at each iteration\
        (Error in the solution). Default: False.
    :param reconstruction_type: Reconstruction type (FBP_CUDA|SIRT_CUDA|\
        SART_CUDA|CGLS_CUDA|FP_CUDA|BP_CUDA|SIRT3D_CUDA|\
        CGLS3D_CUDA). Default: 'FBP_CUDA'.
    """

    def __init__(self):
        super(AstraReconGpu, self).__init__("AstraReconGpu")
        self.GPU_index = None
        self.res = False

    def get_parameters(self):
        return [self.parameters['reconstruction_type'],
                self.parameters['number_of_iterations']]

    def set_options(self, cfg):
        if 'option' not in cfg.keys():
            cfg['option'] = {}
        cfg['option']['GPUindex'] = self.parameters['GPU_index']
        return cfg

    def dynamic_data_info(self):
        alg = self.parameters['reconstruction_type']
        if self.parameters['res_norm'] is True and 'FBP' not in alg:
            self.res = True
            self.nOut += 1
            self.parameters['out_datasets'].append('res_norm')

    def astra_setup(self):
        options_list = ["FBP_CUDA", "SIRT_CUDA", "SART_CUDA", "CGLS_CUDA",
                        "FP_CUDA", "BP_CUDA", "SIRT3D_CUDA", "CGLS3D_CUDA"]
        if not options_list.count(self.parameters['reconstruction_type']):
            raise Exception("Unknown Astra GPU algorithm.")

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
