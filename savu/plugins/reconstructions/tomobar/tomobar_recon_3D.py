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
.. module:: tomobar_recon_3D
   :platform: Unix
   :synopsis: A wrapper around TOmographic MOdel-BAsed Reconstruction (ToMoBAR) software \
   for advanced iterative image reconstruction using _3D_ capabilities of regularisation. \
   This plugin will divide 3D projection data into overlapping subsets using padding.

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.plugins.driver.gpu_plugin import GpuPlugin

import numpy as np
from tomobar.methodsIR import RecToolsIR
from savu.plugins.utils import register_plugin


@register_plugin
class TomobarRecon3d(BaseRecon, GpuPlugin):

    def __init__(self):
        super(TomobarRecon3d, self).__init__("TomobarRecon3d")

    def _get_output_size(self, in_data):
        sizeX = tuple(self.parameters['output_size'])
        shape = in_data.get_shape()
        if sizeX == 'auto':
            detX = in_data.get_data_dimension_by_axis_label('detector_x')
            sizeX = shape[detX]
        return sizeX

    def set_filter_padding(self, in_pData, out_pData):
        self.pad = self.parameters['padding']
        in_data = self.get_in_datasets()[0]
        det_y = in_data.get_data_dimension_by_axis_label('detector_y')
        pad_det_y = '%s.%s' % (det_y, self.pad)
        pad_dict = {'pad_directions': [pad_det_y], 'pad_mode': 'edge'}
        in_pData[0].padding = pad_dict
        out_pData[0].padding = pad_dict

    def setup(self):
        in_dataset = self.get_in_datasets()[0]
        self.parameters['vol_shape'] = tuple(self.parameters['output_size'])
        procs = self.exp.meta_data.get("processes")
        procs = len([i for i in procs if 'GPU' in i])
        dim = in_dataset.get_data_dimension_by_axis_label('detector_y')
        nSlices = int(np.ceil(in_dataset.get_shape()[dim]/float(procs)))
        self._set_max_frames(nSlices)
        super(TomobarRecon3d, self).setup()

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        out_pData = self.get_plugin_out_datasets()[0]
        detY = in_pData.get_data_dimension_by_axis_label('detector_y')
        # ! padding vertical detector !
        self.Vert_det = in_pData.get_shape()[detY] + 2*self.pad

        in_pData = self.get_plugin_in_datasets()
        self.det_dimX_ind = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        self.det_dimY_ind = in_pData[0].get_data_dimension_by_axis_label('detector_y')
        self.output_size = out_pData.get_shape()[self.det_dimX_ind]

            # extract given parameters into dictionaries suitable for ToMoBAR input
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
                                'device_regulariser' : self.parameters['regularisation_device'],
                                'edge_threhsold' : self.parameters['regularisation_edge_thresh'],
                                'time_marching_step' : self.parameters['regularisation_timestep'],
                                'regul_param2' : self.parameters['regularisation_parameter2'],
                                'PD_LipschitzConstant' : self.parameters['regularisation_PD_lip'],
                                'NDF_penalty' : self.parameters['regularisation_NDF_penalty'],
                                'methodTV' : self.parameters['regularisation_methodTV']}

    def process_frames(self, data):
        cor, angles, self.vol_shape, init = self.get_frame_params()

        self.anglesRAD = np.deg2rad(angles.astype(np.float32))
        projdata3D = data[0].astype(np.float32)
        dim_tuple = np.shape(projdata3D)
        self.Horiz_det = dim_tuple[self.det_dimX_ind]
        half_det_width = 0.5*self.Horiz_det
        cor_astra = half_det_width - cor[0]
        projdata3D[projdata3D > 10**15] = 0.0
        projdata3D =np.swapaxes(projdata3D,0,1)
        #print(f"Shape of projdata3D is {np.shape(projdata3D)}")
        self._data_.update({'projection_norm_data' : projdata3D})

        # if one selects PWLS or SWLS models then raw data is also required (2 inputs)
        if ((self.parameters['data_fidelity'] == 'PWLS') or (self.parameters['data_fidelity'] == 'SWLS')):
            rawdata3D = data[1].astype(np.float32)
            rawdata3D[rawdata3D > 10**15] = 0.0
            rawdata3D = np.swapaxes(rawdata3D,0,1)/np.max(np.float32(rawdata3D))
            #print(f"Shape of rawdata3D is {np.shape(rawdata3D)}")
            self._data_.update({'projection_raw_data' : rawdata3D})
            self._data_.update({'beta_SWLS' : self.parameters['data_beta_SWLS']*np.ones(self.Horiz_det)})

       # set parameters and initiate a TomoBar class object
        self.Rectools = RecToolsIR(DetectorsDimH = self.Horiz_det,  # DetectorsDimH # detector dimension (horizontal)
                    DetectorsDimV = self.Vert_det,  # DetectorsDimV # detector dimension (vertical) for 3D case only
                    CenterRotOffset = cor_astra.item() - 0.5, # The center of rotation (CoR) scalar or a vector
                    AnglesVec = self.anglesRAD, # the vector of angles in radians
                    ObjSize = self.output_size, # a scalar to define the reconstructed object dimensions
                    datafidelity=self.parameters['data_fidelity'],# data fidelity, choose LS, PWLS, SWLS
                    device_projector='gpu')

        # Run FISTA reconstrucion algorithm here
        recon = self.Rectools.FISTA(self._data_, self._algorithm_, self._regularisation_)
        recon = np.swapaxes(recon, 0, 1)
        return recon

    def nInput_datasets(self):
        return max(len(self.parameters['in_datasets']), 1)

    def nOutput_datasets(self):
        return 1

    def _set_max_frames(self, frames):
        self._max_frames = frames

    def get_max_frames(self):
        return self._max_frames

    def get_slice_axis(self):
        return 'detector_y'
