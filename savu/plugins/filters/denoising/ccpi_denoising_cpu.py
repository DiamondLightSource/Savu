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
.. module:: Wrapper for CCPi-Regularisation Toolkit (CPU) for efficient 2D/3D denoising
   :platform: Unix
   :synopsis: CCPi-Regularisation/denoising Toolkit delivers a variety of variational 2D/3D denoising methods. The available methods are:  'ROF_TV','FGP_TV' (default),'SB_TV','TGV','LLT_ROF','NDF','Diff4th'

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

from ccpi.filters.regularisers import ROF_TV, FGP_TV, SB_TV, PD_TV, LLT_ROF, TGV, NDF, Diff4th
from ccpi.filters.regularisers import PatchSelect, NLTV
from savu.data.plugin_list import CitationInformation


@register_plugin
class CcpiDenoisingCpu(Plugin, CpuPlugin):
    """
    'ROF_TV': Rudin-Osher-Fatemi Total Variation model;
    'FGP_TV': Fast Gradient Projection Total Variation model;
    'SB_TV': Split Bregman Total Variation model;
    'PD_TV': Primal-Dual Total variation model;
    'NLTV': Nonlocal Total Variation model;
    'TGV': Total Generalised Variation model;
    'LLT_ROF': Lysaker, Lundervold and Tai model combined with Rudin-Osher-Fatemi;
    'NDF': Nonlinear/Linear Diffusion model (Perona-Malik, Huber or Tukey);
    'DIFF4th': Fourth-order nonlinear diffusion model

    :param method: Choose methods |ROF_TV|FGP_TV|SB_TV|NLTV|TGV|LLT_ROF|NDF|Diff4th. Default: 'FGP_TV'.
    :param reg_par: Regularisation (smoothing) parameter. Default: 0.01.
    :param max_iterations: Total number of iterations. Default: 300.
    :param time_step: Time marching step, relevant for ROF_TV, LLT_ROF,\
     NDF, DIFF4th methods. Default: 0.001.
    :param lipshitz_constant: TGV method, Lipshitz constant. Default: 12.
    :param alpha1: TGV method, parameter to control the 1st-order term. Default: 1.0.
    :param alpha0: TGV method, parameter to control the 2nd-order term. Default: 2.0.
    :param reg_parLLT: LLT-ROF method, parameter to control the 2nd-order term. Default: 0.05.
    :param penalty_type: NDF method, Penalty type for the duffison, choose from\
    huber, perona, tukey, constr, constrhuber. Default: 'huber'.
    :param edge_par: NDF and Diff4th methods, noise magnitude parameter. Default: 0.01.
    :param tolerance_constant: tolerance constant to stop iterations earlier. Default: 0.0.
    :param pattern: pattern to apply this to. Default: "VOLUME_XZ".
    """

    def __init__(self):
        super(CcpiDenoisingCpu, self).__init__('CcpiDenoisingCpu')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def pre_process(self):
        # Ccpi-RGL toolkit modules
        self.device = 'cpu'
        if (self.parameters['method'] == 'ROF_TV'):
            # set parameters for the ROF-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_par'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'time_marching_parameter': self.parameters['time_step'], \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'FGP_TV'):
            # set parameters for the FGP-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_par'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'tolerance_constant': self.parameters['tolerance_constant'], \
                         'methodTV': 0, \
                         'nonneg': 0}
        if (self.parameters['method'] == 'SB_TV'):
            # set parameters for the SB-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_par'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'tolerance_constant': self.parameters['tolerance_constant'], \
                         'methodTV': 0}
        if (self.parameters['method'] == 'TGV'):
            # set parameters for the TGV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_par'], \
                         'alpha1': self.parameters['alpha1'], \
                         'alpha0': self.parameters['alpha0'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'LipshitzConstant': self.parameters['lipshitz_constant'], \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'LLT_ROF'):
            # set parameters for the LLT-ROF method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_par'], \
                         'regularisation_parameterLLT': self.parameters['reg_parLLT'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'time_marching_parameter': self.parameters['time_step'], \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'NDF'):
            # set parameters for the NDF method
            if (self.parameters['penalty_type'] == 'huber'):
                # Huber function for the diffusivity
                penaltyNDF = 1
            if (self.parameters['penalty_type'] == 'perona'):
                # Perona-Malik function for the diffusivity
                penaltyNDF = 2
            if (self.parameters['penalty_type'] == 'tukey'):
                # Tukey Biweight function for the diffusivity
                penaltyNDF = 3
            if (self.parameters['penalty_type'] == 'constr'):
                #  Threshold-constrained linear diffusion
                penaltyNDF = 4
            if (self.parameters['penalty_type'] == 'constrhuber'):
                #  Threshold-constrained huber diffusion
                penaltyNDF = 5
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_par'], \
                         'edge_parameter': self.parameters['edge_par'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'time_marching_parameter': self.parameters['time_step'], \
                         'penalty_type': penaltyNDF, \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'Diff4th'):
            # set parameters for the DIFF4th method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_par'], \
                         'edge_parameter': self.parameters['edge_par'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'time_marching_parameter': self.parameters['time_step'], \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'NLTV'):
            # set parameters for the NLTV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_par'], \
                         'edge_parameter': self.parameters['edge_par'], \
                         'number_of_iterations': self.parameters['max_iterations']}
        return self.pars

    # print "The full data shape is", self.get_in_datasets()[0].get_shape()
    # print "Example is", self.parameters['example']
    def process_frames(self, data):
        import numpy as np
        # input_temp = data[0]
        # indices = np.where(np.isnan(input_temp))
        # input_temp[indices] = 0.0
        # self.pars['input'] = input_temp
        input_temp = np.nan_to_num(data[0])
        input_temp[input_temp > 10 ** 15] = 0.0
        self.pars['input'] = input_temp
        # self.pars['input'] = np.nan_to_num(data[0])

        # Running Ccpi-RGLTK modules on GPU
        if (self.parameters['method'] == 'ROF_TV'):
            (im_res, infogpu) = ROF_TV(self.pars['input'],
                                       self.pars['regularisation_parameter'],
                                       self.pars['number_of_iterations'],
                                       self.pars['time_marching_parameter'],
                                       self.pars['tolerance_constant'],
                                       self.device)
        if (self.parameters['method'] == 'FGP_TV'):
            (im_res, infogpu) = FGP_TV(self.pars['input'],
                                       self.pars['regularisation_parameter'],
                                       self.pars['number_of_iterations'],
                                       self.pars['tolerance_constant'],
                                       self.pars['methodTV'],
                                       self.pars['nonneg'], self.device)
        if (self.parameters['method'] == 'SB_TV'):
            (im_res, infogpu) = SB_TV(self.pars['input'],
                                      self.pars['regularisation_parameter'],
                                      self.pars['number_of_iterations'],
                                      self.pars['tolerance_constant'],
                                      self.pars['methodTV'], self.device)
        if (self.parameters['method'] == 'TGV'):
            (im_res, infogpu) = TGV(self.pars['input'],
                                    self.pars['regularisation_parameter'],
                                    self.pars['alpha1'],
                                    self.pars['alpha0'],
                                    self.pars['number_of_iterations'],
                                    self.pars['LipshitzConstant'],
                                    self.pars['tolerance_constant'], self.device)
        if (self.parameters['method'] == 'LLT_ROF'):
            (im_res, infogpu) = LLT_ROF(self.pars['input'],
                                        self.pars['regularisation_parameter'],
                                        self.pars['regularisation_parameterLLT'],
                                        self.pars['number_of_iterations'],
                                        self.pars['time_marching_parameter'],
                                        self.pars['tolerance_constant'], self.device)
        if (self.parameters['method'] == 'NDF'):
            (im_res, infogpu) = NDF(self.pars['input'],
                                    self.pars['regularisation_parameter'],
                                    self.pars['edge_parameter'],
                                    self.pars['number_of_iterations'],
                                    self.pars['time_marching_parameter'],
                                    self.pars['penalty_type'],
                                    self.pars['tolerance_constant'], self.device)
        if (self.parameters['method'] == 'DIFF4th'):
            (im_res, infogpu) = Diff4th(self.pars['input'],
                                        self.pars['regularisation_parameter'],
                                        self.pars['edge_parameter'],
                                        self.pars['number_of_iterations'],
                                        self.pars['time_marching_parameter'],
                                        self.pars['tolerance_constant'], self.device)
        if (self.parameters['method'] == 'NLTV'):
            pars_NLTV = {'algorithm': PatchSelect, \
                         'input': self.pars['input'], \
                         'searchwindow': 9, \
                         'patchwindow': 2, \
                         'neighbours': 17, \
                         'edge_parameter': self.pars['edge_parameter']}
            H_i, H_j, Weights = PatchSelect(pars_NLTV['input'],
                                            pars_NLTV['searchwindow'],
                                            pars_NLTV['patchwindow'],
                                            pars_NLTV['neighbours'],
                                            pars_NLTV['edge_parameter'], self.device)
            parsNLTV_init = {'algorithm': NLTV, \
                             'input': pars_NLTV['input'], \
                             'H_i': H_i, \
                             'H_j': H_j, \
                             'H_k': 0, \
                             'Weights': Weights, \
                             'regularisation_parameter': self.pars['regularisation_parameter'], \
                             'iterations': self.pars['number_of_iterations']}
            im_res = NLTV(parsNLTV_init['input'],
                          parsNLTV_init['H_i'],
                          parsNLTV_init['H_j'],
                          parsNLTV_init['H_k'],
                          parsNLTV_init['Weights'],
                          parsNLTV_init['regularisation_parameter'],
                          parsNLTV_init['iterations'])
            del H_i, H_j, Weights
        # print "calling process frames", data[0].shape
        return im_res

    def post_process(self):
        pass

    def get_citation_information(self):
        cite_info1 = CitationInformation()
        cite_info1.name = 'citation1'
        cite_info1.description = \
            (
                "The CCPi-Regularisation toolkit provides a set of variational regularisers (denoisers) which can be embedded in a plug-and-play fashion into proximal splitting methods for image reconstruction. CCPi-RGL comes with algorithms that can satisfy various prior expectations of the reconstructed object, for example being piecewise-constant or piecewise-smooth nature.")
        cite_info1.bibtex = \
            ("@article{kazantsev2019,\n" +
             "title={CCPi-Regularisation Toolkit for computed tomographic image reconstruction with proximal splitting algorithms},\n" +
             "author={Daniil and Kazantsev, Edoardo and Pasca, Martin and Turner, Philip and Withers},\n" +
             "journal={Software X},\n" +
             "volume={9},\n" +
             "number={},\n" +
             "pages={317-323},\n" +
             "year={2019},\n" +
             "publisher={Elsevier}\n" +
             "}")
        cite_info1.endnote = \
            ("%0 Journal Article\n" +
             "%T CCPi-Regularisation Toolkit for computed tomographic image reconstruction with proximal splitting algorithms\n" +
             "%A Kazantsev, Daniil\n" +
             "%A Pasca, Edoardo\n" +
             "%A Turner, Martin\n" +
             "%A Withers, Philip\n" +
             "%J Software X\n" +
             "%V 9\n" +
             "%N \n" +
             "%P 317--323\n" +
             "%@ --\n" +
             "%D 2019\n" +
             "%I Elsevier\n")
        cite_info1.doi = "doi: 10.1016/j.softx.2019.04.003"

        if (self.parameters['method'] == 'ROF_TV'):
            cite_info2 = CitationInformation()
            cite_info2.name = 'citation2'
            cite_info2.description = (
                "Rudin-Osher-Fatemi explicit PDE minimisation method for smoothed Total Variation regulariser")
            cite_info2.bibtex = \
                ("@article{ROF1992,\n" +
                 "title={Nonlinear total variation based noise removal algorithms},\n" +
                 "author={L. Rudin, S. Osher, E. Fatemi},\n" +
                 "journal={Physica D.},\n" +
                 "volume={60},\n" +
                 "number={},\n" +
                 "pages={259--268},\n" +
                 "year={1992},\n" +
                 "publisher={Elsevier}\n" +
                 "}")
            cite_info2.endnote = \
                ("%0 Journal Article\n" +
                 "%T Nonlinear total variation based noise removal algorithms\n" +
                 "%A Rudin, L.\n" +
                 "%A Osher, S.\n" +
                 "%A Fatemi, Fatemi\n" +
                 "%J Physica D.\n" +
                 "%V 60\n" +
                 "%N \n" +
                 "%P 259--268\n" +
                 "%@ \n" +
                 "%D 1992\n" +
                 "%I Elsevier\n")
            cite_info2.doi = "doi: 10.1016/0167-2789(92)90242-F"
        if (self.parameters['method'] == 'FGP_TV'):
            cite_info2 = CitationInformation()
            cite_info2.name = 'citation2'
            cite_info2.description = ("Fast-Gradient-Projection algorithm for Total Variation regulariser")
            cite_info2.bibtex = \
                ("@article{FGP2009,\n" +
                 "title={Fast gradient-based algorithms for constrained total variation image denoising and deblurring problems},\n" +
                 "author={Amir and Beck, Mark and Teboulle},\n" +
                 "journal={IEEE Transactions on Image Processing},\n" +
                 "volume={18},\n" +
                 "number={11},\n" +
                 "pages={2419--2434},\n" +
                 "year={2009},\n" +
                 "publisher={IEEE}\n" +
                 "}")
            cite_info2.endnote = \
                ("%0 Journal Article\n" +
                 "%T Fast gradient-based algorithms for constrained total variation image denoising and deblurring problems\n" +
                 "%A Beck, Amir\n" +
                 "%A Teboulle, Mark.\n" +
                 "%J IEEE Transactions on Image Processing\n" +
                 "%V 18\n" +
                 "%N 11\n" +
                 "%P 2419--2434\n" +
                 "%@ \n" +
                 "%D 2009\n" +
                 "%I IEEE\n")
            cite_info2.doi = "doi: 10.1109/TIP.2009.2028250"
        if (self.parameters['method'] == 'SB_TV'):
            cite_info2 = CitationInformation()
            cite_info2.name = 'citation2'
            cite_info2.description = ("The Split Bregman approach for Total Variation regulariser")
            cite_info2.bibtex = \
                ("@article{SBTV2009,\n" +
                 "title={The split Bregman method for L1-regularized problems},\n" +
                 "author={Tom and Goldstein, Stanley and Osher},\n" +
                 "journal={SIAM journal on imaging sciences},\n" +
                 "volume={2},\n" +
                 "number={2},\n" +
                 "pages={323--343},\n" +
                 "year={2009},\n" +
                 "publisher={SIAM}\n" +
                 "}")
            cite_info2.endnote = \
                ("%0 Journal Article\n" +
                 "%T The split Bregman method for L1-regularized problems\n" +
                 "%A Goldstein, Tom\n" +
                 "%A Osher, Stanley.\n" +
                 "%J SIAM journal on imaging sciences\n" +
                 "%V 2\n" +
                 "%N 2\n" +
                 "%P 323--343\n" +
                 "%@ \n" +
                 "%D 2009\n" +
                 "%I SIAM\n")
            cite_info2.doi = "doi: 10.1137/080725891"
        if (self.parameters['method'] == 'TGV'):
            cite_info2 = CitationInformation()
            cite_info2.name = 'citation2'
            cite_info2.description = ("Total generalized variation regulariser for piecewise-smooth recovery")
            cite_info2.bibtex = \
                ("@article{TGV2010,\n" +
                 "title={Total generalized variation},\n" +
                 "author={Kristian and Bredies, Karl and Kunisch, Thomas and Pock},\n" +
                 "journal={SIAM journal on imaging sciences},\n" +
                 "volume={3},\n" +
                 "number={3},\n" +
                 "pages={492--526},\n" +
                 "year={2010},\n" +
                 "publisher={SIAM}\n" +
                 "}")
            cite_info2.endnote = \
                ("%0 Journal Article\n" +
                 "%T Total generalized variation\n" +
                 "%A Bredies, Kristian\n" +
                 "%A Kunisch, Kurl.\n" +
                 "%A Pock, Thomas.\n" +
                 "%J SIAM journal on imaging sciences\n" +
                 "%V 3\n" +
                 "%N 3\n" +
                 "%P 492--526\n" +
                 "%@ \n" +
                 "%D 2010\n" +
                 "%I SIAM\n")
            cite_info2.doi = "doi: 10.1137/080725891"
        if (self.parameters['method'] == 'LLT_ROF'):
            cite_info2 = CitationInformation()
            cite_info2.name = 'citation2'
            cite_info2.description = ("Combination for ROF model and LLT for piecewise-smooth recovery")
            cite_info2.bibtex = \
                ("@article{ROFLLT2017,\n" +
                 "title={Model-based iterative reconstruction using higher-order regularization of dynamic synchrotron data},\n" +
                 "author={Daniil and Kazantsev, Enyu and Guo, Andre and Phillion, Philip and Withers, Peter and Lee},\n" +
                 "journal={Measurement Science and Technology},\n" +
                 "volume={28},\n" +
                 "number={9},\n" +
                 "pages={094004},\n" +
                 "year={2017},\n" +
                 "publisher={IoP}\n" +
                 "}")
            cite_info2.endnote = \
                ("%0 Journal Article\n" +
                 "%T Model-based iterative reconstruction using higher-order regularization of dynamic synchrotron data\n" +
                 "%A Kazantsev, Daniil\n" +
                 "%A Enyu, Guo.\n" +
                 "%A Phillion, Andre.\n" +
                 "%A Withers, Philip.\n" +
                 "%A Lee, Peter.\n" +
                 "%J Measurement Science and Technology\n" +
                 "%V 28\n" +
                 "%N 9\n" +
                 "%P 094004\n" +
                 "%@ \n" +
                 "%D 2017\n" +
                 "%I IoP\n")
            cite_info2.doi = "doi: 10.1088/1361-6501"
        if (self.parameters['method'] == 'NDF'):
            cite_info2 = CitationInformation()
            cite_info2.name = 'citation2'
            cite_info2.description = ("Nonlinear or linear duffison as a regulariser ")
            cite_info2.bibtex = \
                ("@article{NDF1990,\n" +
                 "title={Scale-space and edge detection using anisotropic diffusion},\n" +
                 "author={Pietro and Perona, Jitendra and Malik},\n" +
                 "journal={IEEE Transactions on pattern analysis and machine intelligence},\n" +
                 "volume={12},\n" +
                 "number={7},\n" +
                 "pages={629--639},\n" +
                 "year={1990},\n" +
                 "publisher={IEEE}\n" +
                 "}")
            cite_info2.endnote = \
                ("%0 Journal Article\n" +
                 "%T Scale-space and edge detection using anisotropic diffusion\n" +
                 "%A Pietro, Perona\n" +
                 "%A Jitendra, Malik.\n" +
                 "%J IEEE Transactions on pattern analysis and machine intelligence\n" +
                 "%V 12\n" +
                 "%N 7\n" +
                 "%P 629--639\n" +
                 "%@ \n" +
                 "%D 1990\n" +
                 "%I IEEE\n")
            cite_info2.doi = "doi: 10.1109/34.56205"
        if (self.parameters['method'] == 'DIFF4th'):
            cite_info2 = CitationInformation()
            cite_info2.name = 'citation2'
            cite_info2.description = ("Anisotropic diffusion of higher order for piecewise-smooth recovery")
            cite_info2.bibtex = \
                ("@article{ADF2011,\n" +
                 "title={An anisotropic fourth-order diffusion filter for image noise removal},\n" +
                 "author={Mohammad Reza and Hajiaboli},\n" +
                 "journal={International Journal of Computer Vision},\n" +
                 "volume={92},\n" +
                 "number={2},\n" +
                 "pages={177--191},\n" +
                 "year={2011},\n" +
                 "publisher={Springer}\n" +
                 "}")
            cite_info2.endnote = \
                ("%0 Journal Article\n" +
                 "%T Anisotropic diffusion of higher order for piecewise-smooth recovery\n" +
                 "%A Mohammad Reza, Hajiaboli\n" +
                 "%J International Journal of Computer Vision\n" +
                 "%V 92\n" +
                 "%N 2\n" +
                 "%P 177--191\n" +
                 "%@ \n" +
                 "%D 2011\n" +
                 "%I Springer\n")
            cite_info2.doi = "doi: 10.1007/s11263-010-0330-1"
        if (self.parameters['method'] == 'NLTV'):
            cite_info2 = CitationInformation()
            cite_info2.name = 'citation2'
            cite_info2.description = (
                "Nonlocal discrete regularization on weighted graphs: a framework for image and manifold processing")
            cite_info2.bibtex = \
                ("@article{abd2008,\n" +
                 "title={Nonlocal discrete regularization on weighted graphs: a framework for image and manifold processing},\n" +
                 "author={Abderrahim and Lezoray and Bougleux},\n" +
                 "journal={IEEE Trans. Image Processing},\n" +
                 "volume={17},\n" +
                 "number={7},\n" +
                 "pages={1047--1060},\n" +
                 "year={2008},\n" +
                 "publisher={IEEE}\n" +
                 "}")
            cite_info2.endnote = \
                ("%0 Journal Article\n" +
                 "%T Nonlocal discrete regularization on weighted graphs: a framework for image and manifold processing\n" +
                 "%A Abderrahim, Lezoray, Bougleux\n" +
                 "%J IEEE Trans. Image Processing\n" +
                 "%V 17\n" +
                 "%N 7\n" +
                 "%P 1047--1060\n" +
                 "%@ \n" +
                 "%D 2008\n" +
                 "%I IEEE\n")
            cite_info2.doi = "doi: 10.1109/TIP.2008.924284"
        return [cite_info1, cite_info2]
