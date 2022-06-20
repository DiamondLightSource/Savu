# Copyright 2018 Diamond Light Source Ltd.
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
.. module:: tomobar_recon
   :platform: Unix
   :synopsis: 'A wrapper around TOmographic MOdel-BAsed Reconstruction (ToMoBAR) software \
        for advanced iterative image reconstruction (2D case) using GPU'

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.plugins.driver.gpu_plugin import GpuPlugin

import numpy as np
from tomobar.methodsIR import RecToolsIR

from savu.plugins.utils import register_plugin

@register_plugin
class TomobarRecon(BaseRecon, GpuPlugin):

    def __init__(self):
        super(TomobarRecon, self).__init__("TomobarRecon")

    def pre_process(self):
        # extract given parameters into dictionaries suitable for ToMoBAR input
        """
        # current parameters not fully working yet
        :param data_any_rings: a parameter to suppress various artifacts including rings and streaks. Default: None.
        :param data_any_rings_winsizes: half window sizes to collect background information [detector, angles, num of projections]. Default: (9,7,0).
        :param data_any_rings_power: a power parameter for Huber model. Default: 1.5.
        'ring_weights_threshold' :  self.parameters['data_any_rings'],
        'ring_tuple_halfsizes' :  self.parameters['data_any_rings_winsizes'],
        'ring_huber_power' :  self.parameters['data_any_rings_power'],
        """
        self._data_ = {'OS_number' : self.parameters['algorithm_ordersubsets'],
                       'huber_threshold' : self.parameters['data_Huber_thresh'],
                       'ringGH_lambda' :  self.parameters['data_full_ring_GH'],
                       'ringGH_accelerate' :  self.parameters['data_full_ring_accelerator_GH']}

        self._algorithm_ = {'iterations' : self.parameters['algorithm_iterations'],
			                'nonnegativity' : self.parameters['algorithm_nonnegativity'],
                            'mask_diameter' : self.parameters['algorithm_mask'],
                            'verbose' : self.parameters['algorithm_verbose']}

        self._regularisation_ = {'method' : self.parameters['regularisation_method'],
                                'regul_param' : self.parameters['regularisation_parameter'],
                                'iterations' : self.parameters['regularisation_iterations'],
                                'device_regulariser' : 'gpu',
                                'edge_threhsold' : self.parameters['regularisation_edge_thresh'],
                                'time_marching_step' : self.parameters['regularisation_timestep'],
                                'regul_param2' : self.parameters['regularisation_parameter2'],
                                'PD_LipschitzConstant' : self.parameters['regularisation_PD_lip'],
                                'NDF_penalty' : self.parameters['regularisation_NDF_penalty'],
                                'methodTV' : self.parameters['regularisation_methodTV']}

    def process_frames(self, data):
        cor, angles, self.vol_shape, init  = self.get_frame_params()
        sinogram = data[0].astype(np.float32)
        anglesTot, self.DetectorsDimH = np.shape(sinogram)
        half_det_width = 0.5*self.DetectorsDimH
        cor_astra = half_det_width - cor
        self.anglesRAD = np.deg2rad(angles.astype(np.float32))
        self._data_.update({'projection_norm_data' : sinogram})

        # if one selects PWLS or SWLS models then raw data is also required (2 inputs)
        if ((self.parameters['data_fidelity'] == 'PWLS') or (self.parameters['data_fidelity'] == 'SWLS')):
            rawdata = data[1].astype(np.float32)
            rawdata /= np.max(rawdata)
            self._data_.update({'projection_raw_data' : rawdata})
            self._data_.update({'beta_SWLS' : self.parameters['data_beta_SWLS']*np.ones(self.DetectorsDimH)})

        # set parameters and initiate the ToMoBAR class object
        self.Rectools = RecToolsIR(DetectorsDimH = self.DetectorsDimH,  # DetectorsDimH # detector dimension (horizontal)
                    DetectorsDimV = None,  # DetectorsDimV # detector dimension (vertical) for 3D case only
                    CenterRotOffset = cor_astra.item() - 0.5, # The center of rotation (CoR) scalar or a vector
                    AnglesVec = self.anglesRAD, # the vector of angles in radians
                    ObjSize = self.vol_shape[0] , # a scalar to define the reconstructed object dimensions
                    datafidelity=self.parameters['data_fidelity'],# data fidelity, choose LS, PWLS, SWLS
                    device_projector=self.parameters['GPU_index'])

        # Run FISTA reconstrucion algorithm here
        recon = self.Rectools.FISTA(self._data_, self._algorithm_, self._regularisation_)
        return recon

    def nInput_datasets(self):
        return max(len(self.parameters['in_datasets']), 1)

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'
