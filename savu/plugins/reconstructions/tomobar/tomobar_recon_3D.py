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
   This plugin will divide 3D projection data into overalpped subsets using padding, which maskes it fast (GPU driver).

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_vector_recon import BaseVectorRecon
from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.gpu_plugin import GpuPlugin

import numpy as np
from tomobar.methodsIR import RecToolsIR
from savu.plugins.utils import register_plugin


@register_plugin
class TomobarRecon3d(BaseVectorRecon, GpuPlugin):
    """
    A Plugin to reconstruct full-field tomographic projection data using state-of-the-art regularised iterative algorithms from \
    the ToMoBAR package. ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA toolbox and the CCPi RGL toolkit: \
    https://github.com/vais-ral/CCPi-Regularisation-Toolkit.

    :param output_size: The dimension of the reconstructed volume (only X-Y dimension). Default: 'auto'.
    :param padding: The amount of pixels to pad each slab of the cropped projection data. Default: 17.
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
    :param regularisation_device: The number of regularisation iterations. Default: 'gpu'.
    :param regularisation_PD_lip: Primal-dual parameter for convergence. Default: 8.
    :param regularisation_methodTV:  0/1 - TV specific isotropic/anisotropic choice. Default: 0.
    :param regularisation_timestep: Time marching parameter, relevant for \
                    (ROF_TV, LLT_ROF, NDF, Diff4th) penalties. Default: 0.003.
    :param regularisation_edge_thresh: Edge (noise) related parameter, relevant for NDF and Diff4th. Default: 0.01.
    :param regularisation_parameter2:  Regularisation (smoothing) value for LLT_ROF method. Default: 0.005.
    :param regularisation_NDF_penalty: NDF specific penalty type Huber, Perona, Tukey. Default: 'Huber'.
    """

    def __init__(self):
        super(TomobarRecon3d, self).__init__("TomobarRecon3d")

    def _get_output_size(self, in_data):
        sizeX = self.parameters['output_size']
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
        in_dataset, out_dataset = self.get_datasets()
        # reduce the data as per data_subset parameter
        self.preview_flag = \
            self.set_preview(in_dataset[0], self.parameters['preview'])

        axis_labels = in_dataset[0].data_info.get('axis_labels')[0]

        dim_volX, dim_volY, dim_volZ = \
            self.map_volume_dimensions(in_dataset[0])

        axis_labels = {in_dataset[0]:
                           [str(dim_volX) + '.voxel_x.voxels',
                            str(dim_volY) + '.voxel_y.voxels',
                            str(dim_volZ) + '.voxel_z.voxels']}

        # specify reconstructed volume dimensions
        self.output_size = self._get_output_size(in_dataset[0])
        shape = list(in_dataset[0].get_shape())
        rot_dim = in_dataset[0].get_data_dimension_by_axis_label(
            'rotation_angle')
        detX_dim = in_dataset[0].get_data_dimension_by_axis_label('detector_x')
        shape[rot_dim] = self.output_size
        shape[detX_dim] = self.output_size

        # if there are only 3 dimensions then add a fourth for slicing
        # It was commented before since we do it for the TRUE fully 3D reconstruction,
        # in this case we need to pad the data
        """
        if len(shape) == 3:
            axis_labels = [0]*4
            axis_labels[dim_volX] = 'voxel_x.voxels'
            axis_labels[dim_volY] = 'voxel_y.voxels'
            axis_labels[dim_volZ] = 'voxel_z.voxels'
            axis_labels[3] = 'scan.number'
            shape.append(1)
        """

        if self.parameters['vol_shape'] == 'fixed':
            shape[dim_volX] = shape[dim_volZ]
        else:
            shape[dim_volX] = self.parameters['vol_shape']
            shape[dim_volZ] = self.parameters['vol_shape']

        if 'resolution' in list(self.parameters.keys()):
            shape[dim_volX] /= self.parameters['resolution']
            shape[dim_volZ] /= self.parameters['resolution']

        out_dataset[0].create_dataset(axis_labels=axis_labels,
                                      shape=tuple(shape))
        out_dataset[0].add_volume_patterns(dim_volX, dim_volY, dim_volZ)

        ndims = list(range(len(shape)))
        core_dims = (dim_volX, dim_volY, dim_volZ)
        slice_dims = tuple(set(ndims).difference(set(core_dims)))
        out_dataset[0].add_pattern(
            'VOLUME_3D', core_dims=core_dims, slice_dims=slice_dims)

        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()

        procs = self.exp.meta_data.get("processes")
        procs = len([i for i in procs if 'GPU' in i])
        dim = in_dataset[0].get_data_dimension_by_axis_label('detector_y')
        nSlices = int(np.ceil(shape[dim]/float(procs)))

        # making it work for a number of inputs
        for i in range(len(in_dataset)):
            in_pData[i].plugin_data_setup('SINOGRAM', nSlices,  slice_axis='detector_y')

        #in_pData[0].plugin_data_setup('SINOGRAM', nSlices, slice_axis='detector_y')
        # in_pData[1].plugin_data_setup('PROJECTION', nSlices) # (for PWLS)

        # set pattern_name and nframes to process for all datasets
        out_pData[0].plugin_data_setup('VOLUME_XZ', nSlices)

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        detY = in_pData.get_data_dimension_by_axis_label('detector_y')
        # ! padding vertical detector !
        self.Vert_det = in_pData.get_shape()[detY] + 2*self.pad

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

        in_pData = self.get_plugin_in_datasets()
        self.det_dimX_ind = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        self.det_dimY_ind = in_pData[0].get_data_dimension_by_axis_label('detector_y')

    def process_frames(self, data):
        cor, angles, self.vol_shape, init = self.get_frame_params()

        self.anglesRAD = np.deg2rad(angles.astype(np.float32))
        projdata3D = data[0].astype(np.float32)
        dim_tuple = np.shape(projdata3D)
        self.Horiz_det = dim_tuple[self.det_dimX_ind]
        half_det_width = 0.5*self.Horiz_det
        cor_astra = half_det_width - cor[0]
        projdata3D[projdata3D > 10**10] = 0.0
        print(np.shape(projdata3D))
        projdata3D =np.swapaxes(projdata3D,0,1)
        self._data_.update({'projection_norm_data' : projdata3D})

        # if one selects PWLS or SWLS models then raw data is also required (2 inputs)
        if ((self.parameters['data_fidelity'] == 'PWLS') or (self.parameters['data_fidelity'] == 'SWLS')):
            rawdata3D = data[1].astype(np.float32)
            print(np.shape(rawdata3D))
            rawdata3D[rawdata3D > 10**15] = 0.0
            rawdata3D = np.swapaxes(rawdata3D,0,1)/np.max(np.float32(rawdata3D))
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
