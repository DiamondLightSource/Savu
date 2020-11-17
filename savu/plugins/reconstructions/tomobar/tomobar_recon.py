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
   :synopsis: A wrapper around TOmographic MOdel-BAsed Reconstruction (ToMoBAR) software \
   for advanced iterative image reconstruction (2D case) using GPU

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.gpu_plugin import GpuPlugin

import numpy as np
from tomobar.methodsIR import RecToolsIR

from savu.plugins.utils import register_plugin

@register_plugin
class TomobarRecon(BaseRecon, GpuPlugin):
    """
    A GPU plugin to reconstruct full-field tomographic projection data using state-of-the-art regularised iterative algorithms from \
    the ToMoBAR package. ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA toolbox and the CCPi RGL toolkit: \
    https://github.com/vais-ral/CCPi-Regularisation-Toolkit.

    :param output_size: Number of rows and columns in the \
        reconstruction. Default: 'auto'.
    :param data_fidelity: Data fidelity, choose LS, PWLS, SWLS or KL. Default: 'LS'.
    :param data_Huber_thresh: Threshold parameter for __Huber__ data fidelity . Default: None.
    :param data_beta_SWLS: A parameter for stripe-weighted model. Default: 0.1.
    :param data_full_ring_GH: Regularisation variable for full constant ring removal (GH model). Default: None.
    :param data_full_ring_accelerator_GH: Acceleration constant for GH ring removal. Default: 10.0.
    :param algorithm_iterations: Number of outer iterations for FISTA (default) or ADMM methods. Default: 20.
    :param algorithm_verbose: print iterations number and other messages ('off' by default). Default: 'off'.
    :param algorithm_mask: set to 1.0 to enable a circular mask diameter or < 1.0 to shrink the mask. Default: 1.0.
    :param algorithm_ordersubsets: The number of ordered-subsets to accelerate reconstruction. Default: 6.
    :param algorithm_nonnegativity: ENABLE or DISABLE nonnegativity constraint. Default: 'ENABLE'.
    :param regularisation_method: To regularise choose methods ROF_TV, FGP_TV, PD_TV, SB_TV, LLT_ROF,\
                             NDF, TGV, NLTV, Diff4th. Default: 'FGP_TV'.
    :param regularisation_parameter: Regularisation (smoothing) value, higher \
                            the value stronger the smoothing effect. Default: 0.00001.
    :param regularisation_iterations: The number of regularisation iterations. Default: 80.
    :param regularisation_PD_lip: Primal-dual parameter for convergence. Default: 8.
    :param regularisation_methodTV:  0/1 - TV specific isotropic/anisotropic choice. Default: 0.
    :param regularisation_timestep: Time marching parameter, relevant for \
                    (ROF_TV, LLT_ROF, NDF, Diff4th) penalties. Default: 0.003.
    :param regularisation_edge_thresh: Edge (noise) related parameter, relevant for NDF and Diff4th. Default: 0.01.
    :param regularisation_parameter2:  Regularisation (smoothing) value for LLT_ROF method. Default: 0.005.
    :param regularisation_NDF_penalty: NDF specific penalty type Huber, Perona, Tukey. Default: 'Huber'.
    """

    def __init__(self):
        super(TomobarRecon, self).__init__("TomobarRecon")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()

        self.preview_flag = \
            self.set_preview(in_dataset[0], self.parameters['preview'])

        for i in range(len(in_dataset)):
            in_pData[i].plugin_data_setup('SINOGRAM', 'single')

        axis_labels = in_dataset[0].data_info.get('axis_labels')[0]

        dim_volX, dim_volY, dim_volZ = \
            self.map_volume_dimensions(in_dataset[0])

        axis_labels = [0]*3
        axis_labels = {in_dataset[0]:
                       [str(dim_volX) + '.voxel_x.voxels',
                        str(dim_volY) + '.voxel_y.voxels',
                        str(dim_volZ) + '.voxel_z.voxels']}

        shape = list(in_dataset[0].get_shape())
        if self.parameters['vol_shape'] == 'fixed':
            shape[dim_volX] = shape[dim_volZ]
        else:
            shape[dim_volX] = self.parameters['vol_shape']
            shape[dim_volZ] = self.parameters['vol_shape']

        if 'resolution' in self.parameters.keys():
            shape[dim_volX] /= self.parameters['resolution']
            shape[dim_volZ] /= self.parameters['resolution']

        out_dataset[0].create_dataset(axis_labels=axis_labels,
                                      shape=tuple(shape))
        out_dataset[0].add_volume_patterns(dim_volX, dim_volY, dim_volZ)

        idx = 1
        # initial volume dataset
        if 'init_vol' in self.parameters.keys() and \
                self.parameters['init_vol']:
            self.init_vol = True
            in_pData[1].plugin_data_setup('VOLUME_XZ', self.get_max_frames())
            idx += 1

        # cor dataset
        if isinstance(self.parameters['centre_of_rotation'], str):
            self.cor_as_dataset = True
            in_pData[idx].plugin_data_setup('METADATA', self.get_max_frames())

        # set pattern_name and nframes to process for all datasets
        out_pData[0].plugin_data_setup('VOLUME_XZ', self.get_max_frames())

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
                    device_projector='gpu')

        # Run FISTA reconstrucion algorithm here
        recon = self.Rectools.FISTA(self._data_, self._algorithm_, self._regularisation_)
        return recon

    def nInput_datasets(self):
        return max(len(self.parameters['in_datasets']), 1)

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'

    def get_citation_information(self):
        cite_info1 = CitationInformation()
        cite_info1.name = 'citation1'
        cite_info1.description = \
            ("First-order optimisation algorithm for linear inverse problems.")
        cite_info1.bibtex = \
            ("@article{beck2009,\n" +
             "title={A fast iterative shrinkage-thresholding algorithm for linear inverse problems},\n" +
             "author={Amir and Beck, Mark and Teboulle},\n" +
             "journal={SIAM Journal on Imaging Sciences},\n" +
             "volume={2},\n" +
             "number={1},\n" +
             "pages={183--202},\n" +
             "year={2009},\n" +
             "publisher={SIAM}\n" +
             "}")
        cite_info1.endnote = \
            ("%0 Journal Article\n" +
             "%T A fast iterative shrinkage-thresholding algorithm for linear inverse problems\n" +
             "%A Beck, Amir\n" +
             "%A Teboulle, Mark\n" +
             "%J SIAM Journal on Imaging Sciences\n" +
             "%V 2\n" +
             "%N 1\n" +
             "%P 183--202\n" +
             "%@ --\n" +
             "%D 2009\n" +
             "%I SIAM\n")
        cite_info1.doi = "doi: "
        return cite_info1
