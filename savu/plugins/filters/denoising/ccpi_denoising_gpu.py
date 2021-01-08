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
.. module:: ccpi_denoising_gpu
   :platform: Unix
   :synopsis: GPU modules of CCPi-Regularisation Toolkit (CcpiRegulToolkitCpu)

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin

from ccpi.filters.regularisers import ROF_TV, FGP_TV, SB_TV, PD_TV, LLT_ROF, TGV, NDF, Diff4th
from ccpi.filters.regularisers import PatchSelect, NLTV

@register_plugin
class CcpiDenoisingGpu(Plugin, GpuPlugin):
    """
    'ROF_TV': Rudin-Osher-Fatemi Total Variation model;
    'FGP_TV': Fast Gradient Projection Total Variation model;
    'SB_TV': Split Bregman Total Variation model;
    'NLTV': Nonlocal Total Variation model;
    'TGV': Total Generalised Variation model;
    'LLT_ROF': Lysaker, Lundervold and Tai model combined with Rudin-Osher-Fatemi;
    'NDF': Nonlinear/Linear Diffusion model (Perona-Malik, Huber or Tukey);
    'DIFF4th': Fourth-order nonlinear diffusion model

    :param method: Choose methods |ROF_TV|FGP_TV|SB_TV|NLTV|TGV|LLT_ROF|NDF|Diff4th. Default: 'FGP_TV'.
    :param reg_par: Regularisation (smoothing) parameter. Default: 0.01.
    :param max_iterations: Total number of iterations. Default: 300.
    :param time_step: Time marching step, relevant for ROF_TV, LLT_ROF,\
     NDF, Diff4th methods. Default: 0.001.
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
        super(CcpiDenoisingGpu, self).__init__('CcpiDenoisingGpu')
        self.GPU_index = None
        self.res = False
        self.start = 0

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
        self.device = 'gpu'
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
            # set parameters for the Diff4th method
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

