# Copyright 2019 Diamond Light Source Ltd.
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
.. module:: ccpi_denoising_gpu_3D
   :platform: Unix
   :synopsis: GPU modules of CCPi-Regularisation Toolkit (CcpiRegulToolkitGpu)

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin
import numpy as np
import subprocess as sp
from savu.core.iterate_plugin_group_utils import enable_iterative_loop, \
    check_if_end_plugin_in_iterate_group, setup_extra_plugin_data_padding

from ccpi.filters.regularisers import ROF_TV, FGP_TV, SB_TV, PD_TV, LLT_ROF, TGV, NDF, Diff4th
from ccpi.filters.regularisers import PatchSelect, NLTV


@register_plugin
class CcpiDenoisingGpu3d(Plugin, GpuPlugin):

    def __init__(self):
        super(CcpiDenoisingGpu3d, self).__init__("CcpiDenoisingGpu3d")
        self.slice_dir = None
        self.device = None

    @setup_extra_plugin_data_padding
    def set_filter_padding(self, in_pData, out_pData):
        self.pad = self.parameters['padding']
        pad_slice_dir = '%s.%s' % (self.slice_dir[0], self.pad)
        pad_dict = {'pad_directions': [pad_slice_dir], 'pad_mode': 'edge'}
        in_pData[0].padding = pad_dict
        out_pData[0].padding = pad_dict

    @enable_iterative_loop
    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        pattern_type = self.parameters['pattern']
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(pattern_type, 'single')
        out_dataset[0].create_dataset(in_dataset[0])
        out_pData[0].plugin_data_setup(pattern_type, 'single')

        self.slice_dir = list(in_dataset[0].get_slice_dimensions())
        procs = self.exp.meta_data.get("processes")
        procs = len([i for i in procs if 'GPU' in i])
        nSlices = int(np.ceil(in_dataset[0].get_shape()[self.slice_dir[0]] / float(procs)))
        core_dims_index = list(in_dataset[0].get_core_dimensions())
        core_dims_size = 1
        for core_index in core_dims_index:
            core_dims_size *= in_dataset[0].get_shape()[core_index]
        # calculate the amount of slices than would fit the GPU memory
        gpu_available_mb = self.get_gpu_memory()[0]/procs  # get the free GPU memory of a first device if many
        slice_size_mbbytes = int(np.ceil((core_dims_size * 1024 * 4) / (1024 ** 3)))
        # calculate the GPU memory required based on 3D regularisation restrictions (avoiding CUDA-error)
        if 'ROF_TV' in self.parameters['method']:
            slice_size_mbbytes *= 8
        if 'FGP_TV' in self.parameters['method']:
            slice_size_mbbytes *= 12
        if 'SB_TV' in self.parameters['method']:
            slice_size_mbbytes *= 10
        if 'PD_TV' in self.parameters['method']:
            slice_size_mbbytes *= 8
        if 'LLT_ROF' in self.parameters['method']:
            slice_size_mbbytes *= 12
        if 'TGV' in self.parameters['method']:
            slice_size_mbbytes *= 15
        if 'NDF' in self.parameters['method']:
            slice_size_mbbytes *= 5
        if 'Diff4th' in self.parameters['method']:
            slice_size_mbbytes *= 5
        if 'NLTV' in self.parameters['method']:
            slice_size_mbbytes *= 8
        slices_fit_total = int(gpu_available_mb / slice_size_mbbytes) - 2*self.parameters['padding']
        if nSlices > slices_fit_total:
            nSlices = slices_fit_total
        self._set_max_frames(nSlices)

    def pre_process(self):
        self.device = 'gpu'
        if self.parameters['method'] == 'ROF_TV':
            # set parameters for the ROF-TV method
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'number_of_iterations': self.parameters['max_iterations'],
                         'time_marching_parameter': self.parameters['time_step'],
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if self.parameters['method'] == 'PD_TV':
            # set parameters for the PD-TV method
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'number_of_iterations': self.parameters['max_iterations'],
                         'tolerance_constant': self.parameters['tolerance_constant'],
                         'methodTV': 0,
                         'nonneg': 0,
                         'PD_LipschitzConstant': 8}
        if self.parameters['method'] == 'FGP_TV':
            # set parameters for the FGP-TV method
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'number_of_iterations': self.parameters['max_iterations'],
                         'tolerance_constant': self.parameters['tolerance_constant'],
                         'methodTV': 0,
                         'nonneg': 0}
        if self.parameters['method'] == 'SB_TV':
            # set parameters for the SB-TV method
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'number_of_iterations': self.parameters['max_iterations'],
                         'tolerance_constant': self.parameters['tolerance_constant'],
                         'methodTV': 0}
        if self.parameters['method'] == 'TGV':
            # set parameters for the TGV method
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'alpha1': self.parameters['alpha1'],
                         'alpha0': self.parameters['alpha0'],
                         'number_of_iterations': self.parameters['max_iterations'],
                         'LipshitzConstant': self.parameters['lipshitz_constant'],
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if self.parameters['method'] == 'LLT_ROF':
            # set parameters for the LLT-ROF method
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'regularisation_parameterLLT': self.parameters['reg_parLLT'],
                         'number_of_iterations': self.parameters['max_iterations'],
                         'time_marching_parameter': self.parameters['time_step'],
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if self.parameters['method'] == 'NDF':
            # set parameters for the NDF method
            if self.parameters['penalty_type'] == 'huber':
                # Huber function for the diffusivity
                penaltyNDF = 1
            if self.parameters['penalty_type'] == 'perona':
                # Perona-Malik function for the diffusivity
                penaltyNDF = 2
            if self.parameters['penalty_type'] == 'tukey':
                # Tukey Biweight function for the diffusivity
                penaltyNDF = 3
            if self.parameters['penalty_type'] == 'constr':
                #  Threshold-constrained linear diffusion
                penaltyNDF = 4
            if self.parameters['penalty_type'] == 'constrhuber':
                #  Threshold-constrained huber diffusion
                penaltyNDF = 5
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'edge_parameter': self.parameters['edge_par'],
                         'number_of_iterations': self.parameters['max_iterations'],
                         'time_marching_parameter': self.parameters['time_step'],
                         'penalty_type': penaltyNDF,
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if self.parameters['method'] == 'Diff4th':
            # set parameters for the Diff4th method
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'edge_parameter': self.parameters['edge_par'],
                         'number_of_iterations': self.parameters['max_iterations'],
                         'time_marching_parameter': self.parameters['time_step'],
                         'tolerance_constant': self.parameters['tolerance_constant']}
        if self.parameters['method'] == 'NLTV':
            # set parameters for the NLTV method
            self.pars = {'algorithm': self.parameters['method'],
                         'regularisation_parameter': self.parameters['reg_parameter'],
                         'edge_parameter': self.parameters['edge_par'],
                         'number_of_iterations': self.parameters['max_iterations']}
        return self.pars

    def process_frames(self, data):
        input_temp = np.nan_to_num(data[0])
        input_temp[input_temp > 10 ** 15] = 0.0
        self.pars['input'] = input_temp
        # Running Ccpi-RGLTK modules on GPU
        if self.parameters['method'] == 'ROF_TV':
            (im_res, infogpu) = ROF_TV(self.pars['input'],
                                       self.pars['regularisation_parameter'],
                                       self.pars['number_of_iterations'],
                                       self.pars['time_marching_parameter'],
                                       self.pars['tolerance_constant'],
                                       self.device)
        if self.parameters['method'] == 'FGP_TV':
            (im_res, infogpu) = FGP_TV(self.pars['input'],
                                       self.pars['regularisation_parameter'],
                                       self.pars['number_of_iterations'],
                                       self.pars['tolerance_constant'],
                                       self.pars['methodTV'],
                                       self.pars['nonneg'], self.device)
        if self.parameters['method'] == 'PD_TV':
            (im_res, infogpu) = PD_TV(self.pars['input'],
                                       self.pars['regularisation_parameter'],
                                       self.pars['number_of_iterations'],
                                       self.pars['tolerance_constant'],
                                       self.pars['methodTV'],
                                       self.pars['nonneg'],
                                       self.pars['PD_LipschitzConstant'],
                                       self.parameters['GPU_index'])                                       
        if self.parameters['method'] == 'SB_TV':
            (im_res, infogpu) = SB_TV(self.pars['input'],
                                      self.pars['regularisation_parameter'],
                                      self.pars['number_of_iterations'],
                                      self.pars['tolerance_constant'],
                                      self.pars['methodTV'], self.device)
        if self.parameters['method'] == 'TGV':
            (im_res, infogpu) = TGV(self.pars['input'],
                                    self.pars['regularisation_parameter'],
                                    self.pars['alpha1'],
                                    self.pars['alpha0'],
                                    self.pars['number_of_iterations'],
                                    self.pars['LipshitzConstant'],
                                    self.pars['tolerance_constant'], self.device)
        if self.parameters['method'] == 'LLT_ROF':
            (im_res, infogpu) = LLT_ROF(self.pars['input'],
                                        self.pars['regularisation_parameter'],
                                        self.pars['regularisation_parameterLLT'],
                                        self.pars['number_of_iterations'],
                                        self.pars['time_marching_parameter'],
                                        self.pars['tolerance_constant'], self.device)
        if self.parameters['method'] == 'NDF':
            (im_res, infogpu) = NDF(self.pars['input'],
                                    self.pars['regularisation_parameter'],
                                    self.pars['edge_parameter'],
                                    self.pars['number_of_iterations'],
                                    self.pars['time_marching_parameter'],
                                    self.pars['penalty_type'],
                                    self.pars['tolerance_constant'], self.device)
        if self.parameters['method'] == 'DIFF4th':
            (im_res, infogpu) = Diff4th(self.pars['input'],
                                        self.pars['regularisation_parameter'],
                                        self.pars['edge_parameter'],
                                        self.pars['number_of_iterations'],
                                        self.pars['time_marching_parameter'],
                                        self.pars['tolerance_constant'], self.device)
        if self.parameters['method'] == 'NLTV':
            pars_NLTV = {'algorithm': PatchSelect,
                         'input': self.pars['input'],
                         'searchwindow': 9,
                         'patchwindow': 2,
                         'neighbours': 17,
                         'edge_parameter': self.pars['edge_parameter']}
            H_i, H_j, Weights = PatchSelect(pars_NLTV['input'],
                                            pars_NLTV['searchwindow'],
                                            pars_NLTV['patchwindow'],
                                            pars_NLTV['neighbours'],
                                            pars_NLTV['edge_parameter'], self.device)
            parsNLTV_init = {'algorithm': NLTV,
                             'input': pars_NLTV['input'],
                             'H_i': H_i,
                             'H_j': H_j,
                             'H_k': 0,
                             'Weights': Weights,
                             'regularisation_parameter': self.pars['regularisation_parameter'],
                             'iterations': self.pars['number_of_iterations']}
            im_res = NLTV(parsNLTV_init['input'],
                          parsNLTV_init['H_i'],
                          parsNLTV_init['H_j'],
                          parsNLTV_init['H_k'],
                          parsNLTV_init['Weights'],
                          parsNLTV_init['regularisation_parameter'],
                          parsNLTV_init['iterations'])
            del H_i, H_j, Weights
        return im_res

    def _set_max_frames(self, frames):
        self._max_frames = frames

    def get_gpu_memory(self):
        command = "nvidia-smi --query-gpu=memory.free --format=csv"
        memory_free_info = sp.check_output(command.split()).decode('ascii').split('\n')[:-1][1:]
        memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]
        return memory_free_values

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    # total number of output datasets
    def nOutput_datasets(self):
        if check_if_end_plugin_in_iterate_group(self.exp):
            return 2
        else:
            return 1

    # total number of output datasets that are clones
    def nClone_datasets(self):
        if check_if_end_plugin_in_iterate_group(self.exp):
            return 1
        else:
            return 0
