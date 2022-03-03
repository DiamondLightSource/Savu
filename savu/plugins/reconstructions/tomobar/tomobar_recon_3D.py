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
from savu.core.iterate_plugin_group_utils import enable_iterative_loop, \
    check_if_end_plugin_in_iterate_group, setup_extra_plugin_data_padding


@register_plugin
class TomobarRecon3d(BaseRecon, GpuPlugin):

    def __init__(self):
        super(TomobarRecon3d, self).__init__("TomobarRecon3d")
        self.Vert_det = None
        self.pad = None

    @setup_extra_plugin_data_padding
    def set_filter_padding(self, in_pData, out_pData):
        self.pad = self.parameters['padding']
        in_data = self.get_in_datasets()[0]
        det_y = in_data.get_data_dimension_by_axis_label('detector_y')
        pad_det_y = '%s.%s' % (det_y, self.pad)
        pad_dict = {'pad_directions': [pad_det_y], 'pad_mode': 'edge'}
        in_pData[0].padding = pad_dict
        out_pData[0].padding = pad_dict
        if len(self.get_in_datasets()) > 1:
            in_pData[1].padding = pad_dict

    @enable_iterative_loop
    def setup(self):
        in_dataset = self.get_in_datasets()[0]
        procs = self.exp.meta_data.get("processes")
        procs = len([i for i in procs if 'GPU' in i])
        dim = in_dataset.get_data_dimension_by_axis_label('detector_y')
        nSlices = int(np.ceil(in_dataset.get_shape()[dim] / float(procs)))
        # calculate the amount of slices than would fit the GPU memory
        gpu_available_mb = self.get_gpu_memory()[0]/procs  # get the free GPU memory of a first device if many
        det_x_dim = in_dataset.get_shape()[in_dataset.get_data_dimension_by_axis_label('detector_x')]
        rot_angles_dim = in_dataset.get_shape()[in_dataset.get_data_dimension_by_axis_label('rotation_angle')]
        slice_size_mbbytes = int(np.ceil(((det_x_dim * det_x_dim) * 1024 * 4) / (1024 ** 3)))
        # calculate the GPU memory required based on 3D regularisation restrictions (avoiding CUDA-error)
        if 'ROF_TV' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 8
        if 'FGP_TV' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 12
        if 'SB_TV' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 10
        if 'PD_TV' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 8
        if 'LLT_ROF' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 12
        if 'TGV' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 15
        if 'NDF' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 5
        if 'Diff4th' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 5
        if 'NLTV' in self.parameters['regularisation_method']:
            slice_size_mbbytes *= 8
        slices_fit_total = int(gpu_available_mb / slice_size_mbbytes) - 2*self.parameters['padding']
        if nSlices > slices_fit_total:
            nSlices = slices_fit_total
        self._set_max_frames(nSlices)
        # get experimental metadata of projection_shifts
        if 'projection_shifts' in list(self.exp.meta_data.dict.keys()):
            self.projection_shifts = self.exp.meta_data.dict['projection_shifts']
        super(TomobarRecon3d, self).setup()

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        out_pData = self.get_plugin_out_datasets()[0]
        detY = in_pData.get_data_dimension_by_axis_label('detector_y')
        # ! padding the vertical detector !
        self.Vert_det = in_pData.get_shape()[detY] + 2 * self.pad

        in_pData = self.get_plugin_in_datasets()
        self.det_dimX_ind = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        self.det_dimY_ind = in_pData[0].get_data_dimension_by_axis_label('detector_y')

        # extract given parameters into dictionaries suitable for ToMoBAR input
        self._data_ = {'OS_number': self.parameters['algorithm_ordersubsets'],
                       'huber_threshold': self.parameters['data_Huber_thresh'],
                       'ringGH_lambda': self.parameters['data_full_ring_GH'],
                       'ringGH_accelerate': self.parameters['data_full_ring_accelerator_GH']}

        self._algorithm_ = {'iterations': self.parameters['algorithm_iterations'],
                            'nonnegativity': self.parameters['algorithm_nonnegativity'],
                            'mask_diameter': self.parameters['algorithm_mask'],
                            'verbose': self.parameters['algorithm_verbose']}

        self._regularisation_ = {'method': self.parameters['regularisation_method'],
                                 'regul_param': self.parameters['regularisation_parameter'],
                                 'iterations': self.parameters['regularisation_iterations'],
                                 'device_regulariser': self.parameters['regularisation_device'],
                                 'edge_threhsold': self.parameters['regularisation_edge_thresh'],
                                 'time_marching_step': self.parameters['regularisation_timestep'],
                                 'regul_param2': self.parameters['regularisation_parameter2'],
                                 'PD_LipschitzConstant': self.parameters['regularisation_PD_lip'],
                                 'NDF_penalty': self.parameters['regularisation_NDF_penalty'],
                                 'methodTV': self.parameters['regularisation_methodTV']}

    def process_frames(self, data):
        cor, angles, self.vol_shape, init = self.get_frame_params()
        self.anglesRAD = np.deg2rad(angles.astype(np.float32))
        projdata3D = data[0].astype(np.float32)
        dim_tuple = np.shape(projdata3D)
        self.Horiz_det = dim_tuple[self.det_dimX_ind]
        half_det_width = 0.5 * self.Horiz_det
        projdata3D[projdata3D > 10 ** 15] = 0.0
        projdata3D = np.swapaxes(projdata3D, 0, 1)
        self._data_.update({'projection_norm_data': projdata3D})

        # dealing with projection shifts and the CoR
        cor_astra = half_det_width - np.mean(cor)
        CenterOffset = cor_astra.item() - 0.5
        if np.sum(self.projection_shifts) != 0.0:
            CenterOffset = np.zeros(np.shape(self.projection_shifts))
            CenterOffset[:, 0] = (cor_astra.item() - 0.5) - self.projection_shifts[:, 0]
            CenterOffset[:, 1] = -self.projection_shifts[:, 1] - 0.5

        # if one selects PWLS or SWLS models then raw data is also required (2 inputs)
        if (self.parameters['data_fidelity'] == 'PWLS') or (self.parameters['data_fidelity'] == 'SWLS'):
            rawdata3D = data[1].astype(np.float32)
            rawdata3D[rawdata3D > 10 ** 15] = 0.0
            rawdata3D = np.swapaxes(rawdata3D, 0, 1) / np.max(np.float32(rawdata3D))
            self._data_.update({'projection_raw_data': rawdata3D})
            self._data_.update({'beta_SWLS': self.parameters['data_beta_SWLS'] * np.ones(self.Horiz_det)})

        # set parameters and initiate a TomoBar class object
        self.Rectools = RecToolsIR(DetectorsDimH=self.Horiz_det,  # DetectorsDimH # detector dimension (horizontal)
                                   DetectorsDimV=self.Vert_det,
                                   # DetectorsDimV # detector dimension (vertical) for 3D case only
                                   CenterRotOffset=CenterOffset,  # The center of rotation (CoR)
                                   AnglesVec=-self.anglesRAD,  # the vector of angles in radians
                                   ObjSize=self.vol_shape[0],  # a scalar to define the reconstructed object dimensions
                                   datafidelity=self.parameters['data_fidelity'],
                                   # data fidelity, choose LS, PWLS, SWLS
                                   device_projector='gpu')

        # Run FISTA reconstruction algorithm here
        recon = self.Rectools.FISTA(self._data_, self._algorithm_, self._regularisation_)
        recon = np.swapaxes(recon, 0, 1)
        return recon

    def nInput_datasets(self):
        return max(len(self.parameters['in_datasets']), 1)

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

    def _set_max_frames(self, frames):
        self._max_frames = frames
