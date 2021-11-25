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
.. module:: iterative_ccpi_denoising
   :platform: Unix
   :synopsis: iterative ccpi denoising with changing patterns between Savu (outer) iterations
.. moduleauthor:: Daniil Kazantsev & Yousef Moazzam <scientificsoftware@diamond.ac.uk>
"""

import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.iterative_plugin import IterativePlugin

from ccpi.filters.regularisers import ROF_TV, FGP_TV, SB_TV, PD_TV, LLT_ROF, TGV, NDF, Diff4th
from ccpi.filters.regularisers import PatchSelect, NLTV


@register_plugin
class IterativeCcpiDenoising(BaseFilter, IterativePlugin):

    def __init__(self):
        super(IterativeCcpiDenoising, self).__init__("IterativeCcpiDenoising")

    def pre_process(self):
        # set Savu external iterations
        self.set_iterations(self.parameters['plugin_iterations'])
        # Ccpi-RGL toolkit modules
        self.device = 'cpu'
        if (self.parameters['method'] == 'ROF_TV'):
            # set parameters for the ROF-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_parameter'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'time_marching_parameter': self.parameters['time_step'], \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'FGP_TV'):
            # set parameters for the FGP-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_parameter'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'tolerance_constant': self.parameters['tolerance_constant'], \
                         'methodTV': 0, \
                         'nonneg': 0}
        if (self.parameters['method'] == 'SB_TV'):
            # set parameters for the SB-TV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_parameter'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'tolerance_constant': self.parameters['tolerance_constant'], \
                         'methodTV': 0}
        if (self.parameters['method'] == 'TGV'):
            # set parameters for the TGV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_parameter'], \
                         'alpha1': self.parameters['alpha1'], \
                         'alpha0': self.parameters['alpha0'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'LipshitzConstant': self.parameters['lipshitz_constant'], \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'LLT_ROF'):
            # set parameters for the LLT-ROF method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_parameter'], \
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
                         'regularisation_parameter': self.parameters['reg_parameter'], \
                         'edge_parameter': self.parameters['edge_par'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'time_marching_parameter': self.parameters['time_step'], \
                         'penalty_type': penaltyNDF, \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'Diff4th'):
            # set parameters for the DIFF4th method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_parameter'], \
                         'edge_parameter': self.parameters['edge_par'], \
                         'number_of_iterations': self.parameters['max_iterations'], \
                         'time_marching_parameter': self.parameters['time_step'], \
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if (self.parameters['method'] == 'NLTV'):
            # set parameters for the NLTV method
            self.pars = {'algorithm': self.parameters['method'], \
                         'regularisation_parameter': self.parameters['reg_parameter'], \
                         'edge_parameter': self.parameters['edge_par'], \
                         'number_of_iterations': self.parameters['max_iterations']}
        return self.pars

    def process_frames(self, data):
        input_temp = np.nan_to_num(data[0])
        input_temp[input_temp > 10 ** 15] = 0.0
        self.pars['input'] = input_temp

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
        # option here to break out of the iterations
        #self.set_processing_complete()
        pass

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_XZ', 'single')

        # Cloned datasets are at the end of the out_dataset list
        out_dataset[0].create_dataset(in_dataset[0])

        # What is a cloned dataset?
        # Since each dataset in Savu has its own backing hdf5 file, a dataset
        # cannot be used for input and output at the same time.  So, in the
        # case of iterative plugins, if a dataset is used as output and then
        # as input on the next iteration, the subsequent output must be a
        # different file.
        # A cloned dataset is a copy of another dataset but with a different
        # backing file.  It doesn't have a name, is not accessible as a dataset
        # in the framework and is only used in alternation with another
        # dataset to allow it to be used as both input and output
        # simultaneously.

        # This is a cloned dataset (of out_dataset[0])
        self.create_clone(out_dataset[1], out_dataset[0])

        out_pData[0].plugin_data_setup('VOLUME_XZ', 'single')
        out_pData[1].plugin_data_setup('VOLUME_XZ', 'single')

        # input and output datasets for the first iteration
        self.set_iteration_datasets(0, [in_dataset[0]], [out_dataset[0]])
        # input and output datasets for subsequent iterations
        self.set_iteration_datasets(1, [in_dataset[0], out_dataset[0]],
                                    [out_dataset[1]])
        # out_dataset[0] and out_dataset[1] will continue to alternate for
        # all remaining iterations i.e. output becomes input and input becomes
        # output.

    # total number of output datasets
    def nOutput_datasets(self):
        return 2

    # total number of output datasets that are clones
    def nClone_datasets(self):
        return 1
