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
.. module:: tomobar_recon3D
   :platform: Unix
   :synopsis: A wrapper around TOmographic MOdel-BAsed Reconstruction (ToMoBAR) software \
   for advanced iterative image reconstruction using _3D_ capabilities of regularisation. \
   The plugin will run on one node and can be slow. 

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation
#from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.driver.multi_threaded_plugin import MultiThreadedPlugin


import numpy as np
# TOmographic MOdel-BAsed Reconstruction (ToMoBAR)
# https://github.com/dkazanc/ToMoBAR
from tomobar.methodsIR import RecToolsIR

from savu.plugins.utils import register_plugin
#from scipy import ndimage

@register_plugin
class TomobarRecon3d(BaseRecon, MultiThreadedPlugin):
    """
    A Plugin to reconstruct full-field tomographic projection data using state-of-the-art regularised iterative algorithms from \
    the ToMoBAR package. ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA toolbox and the CCPi RGL toolkit: \
    https://github.com/vais-ral/CCPi-Regularisation-Toolkit.

    :param output_size: The dimension of the reconstructed volume (cube). Default: 'auto'.
    :param iterations: Number of outer iterations for FISTA method. Default: 20.
    :param datafidelity: Data fidelity, Least Squares only at the moment. Default: 'LS'.
    :param nonnegativity: Nonnegativity constraint, choose Enable or None. Default: 'ENABLE'.
    :param ordersubsets: The number of ordered-subsets to accelerate reconstruction. Default: 6.
    :param converg_const: Lipschitz constant, can be set to a value or automatic calculation. Default: 'power'.
    :param regularisation: To regularise choose methods ROF_TV, FGP_TV, SB_TV, LLT_ROF,\
                             NDF, Diff4th. Default: 'FGP_TV'.
    :param regularisation_parameter: Regularisation (smoothing) value, higher \
                            the value stronger the smoothing effect. Default: 0.001.
    :param regularisation_iterations: The number of regularisation iterations. Default: 300.
    :param time_marching_parameter: Time marching parameter, relevant for \
                    (ROF_TV, LLT_ROF, NDF, Diff4th) penalties. Default: 0.0025.
    :param edge_param: Edge (noise) related parameter, relevant for NDF and Diff4th. Default: 0.01.
    :param regularisation_parameter2:  Regularisation (smoothing) value for LLT_ROF method. Default: 0.005.
    :param NDF_penalty: NDF specific penalty type Huber, Perona, Tukey. Default: 'Huber'.
    :param tolerance: Tolerance to stop outer iterations earlier. Default: 1e-9.
    :param ring_variable: Regularisation variable for ring removal. Default: 0.0.
    :param ring_accelerator: Acceleration constant for ring removal (use with care). Default: 50.0.
    """

    def __init__(self):
        super(TomobarRecon3d, self).__init__("TomobarRecon3d")

    def _get_output_size(self, in_data):
        size = self.parameters['output_size']
        if size == 'auto':
            shape = in_data.get_shape()
            detX = in_data.get_data_dimension_by_axis_label('detector_x')
            size = shape[detX]
        return size
    
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

        self.output_size = self._get_output_size(in_dataset[0])
        shape = [0]*len(in_dataset[0].get_shape())
        # ! A TEMPORAL FIX !
#        for dim in [dim_volX, dim_volY, dim_volZ]:
#            shape[dim] = self.output_size
        shape[0] = self.output_size
        shape[1] = 135
        shape[2] = self.output_size


        # if there are only 3 dimensions then add a fourth for slicing
        if len(shape) == 3:
            axis_labels = [0]*4
            axis_labels[dim_volX] = 'voxel_x.voxels'
            axis_labels[dim_volY] = 'voxel_y.voxels'
            axis_labels[dim_volZ] = 'voxel_z.voxels'
            axis_labels[3] = 'scan.number'
            shape.append(1)

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
        
        ndims = range(len(shape))
        core_dims = (dim_volX, dim_volY, dim_volZ)
        slice_dims = tuple(set(ndims).difference(set(core_dims)))
        out_dataset[0].add_pattern(
                'VOLUME_3D', core_dims=core_dims, slice_dims=slice_dims)

        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()

        dim = in_dataset[0].get_data_dimension_by_axis_label('rotation_angle')
        nSlices = in_dataset[0].get_shape()[dim]
        #in_pData[0].plugin_data_setup('PROJECTION', nSlices,
        #        slice_axis='rotation_angle')
        in_pData[0].plugin_data_setup('PROJECTION', nSlices)
        
        # set pattern_name and nframes to process for all datasets
        out_pData[0].plugin_data_setup('VOLUME_3D', 'single')
   
    def pre_process(self):
        # extract given parameters
        self.iterationsFISTA = self.parameters['iterations']
        self.datafidelity = self.parameters['datafidelity']
        self.nonnegativity = self.parameters['nonnegativity']
        self.ordersubsets = self.parameters['ordersubsets']
        self.converg_const = self.parameters['converg_const']
        self.regularisation = self.parameters['regularisation']
        self.regularisation_parameter = self.parameters['regularisation_parameter']
        self.regularisation_parameter2 = self.parameters['regularisation_parameter2']
        self.ring_variable = self.parameters['ring_variable']
        self.ring_accelerator = self.parameters['ring_accelerator']
        self.time_marching_parameter = self.parameters['time_marching_parameter']
        self.edge_param = self.parameters['edge_param']
        self.NDF_penalty = self.parameters['NDF_penalty']
        self.tolerance = self.parameters['tolerance']
        
        self.RecToolsIR = None
        if (self.ordersubsets > 1):
            self.regularisation_iterations = (int)(self.parameters['regularisation_iterations']/self.ordersubsets) + 1
        else:
            self.regularisation_iterations = self.parameters['regularisation_iterations']
            
        in_data = self.get_in_datasets()[0]
        self.detector_x = in_data.get_data_dimension_by_axis_label('detector_x')
        self.detector_y = in_data.get_data_dimension_by_axis_label('detector_y')

    def process_frames(self, data):
        centre_of_rotations, angles, self.vol_shape, init  = self.get_frame_params()
        
        self.anglesRAD = np.deg2rad(angles.astype(np.float32))
        self.centre_of_rotations = centre_of_rotations
        projdata3D = data[0].astype(np.float32)
        dim_tuple = np.shape(projdata3D)
        self.Horiz_det = dim_tuple[self.detector_x]
        self.Vert_det = dim_tuple[self.detector_y]
        
        #temp = np.random.rand(160, 160, 160)
        
        # print(self.centre_of_rotations)
        projdata3D =np.swapaxes(projdata3D,0,1)
        
        # check if the reconstruction class has been initialised and calculate 
        # Lipschitz constant if not given explicitly
        self.setup_Lipschitz_constant()
        
        # print(self.Lipschitz_const)
        # Run FISTA reconstrucion algorithm here
        recon = self.Rectools.FISTA(projdata3D,\
                                    iterationsFISTA = self.iterationsFISTA,\
                                    regularisation = self.regularisation,\
                                    regularisation_parameter = self.regularisation_parameter,\
                                    regularisation_iterations = self.regularisation_iterations,\
                                    regularisation_parameter2 = self.regularisation_parameter2,\
                                    time_marching_parameter = self.time_marching_parameter,\
                                    lambdaR_L1 = self.ring_variable,\
                                    alpha_ring = self.ring_accelerator,\
                                    NDF_penalty = self.NDF_penalty,\
                                    tolerance_regul = 0.0,\
                                    edge_param = self.edge_param,\
                                    lipschitz_const = self.Lipschitz_const)
        recon = np.swapaxes(recon,0,1) # temporal fix!
        #print(np.shape(recon))
        #recon = np.newaxis(recon, axis=3)
        return recon
    
    def setup_Lipschitz_constant(self):
        if self.RecToolsIR is not None:
            return 
        
       # set parameters and initiate a TomoBar class object
        self.Rectools = RecToolsIR(DetectorsDimH = self.Horiz_det,  # DetectorsDimH # detector dimension (horizontal)
                    DetectorsDimV = self.Vert_det,  # DetectorsDimV # detector dimension (vertical) for 3D case only
                    CenterRotOffset = 0.0, # Center of Rotation (CoR) scalar (for 3D case only)
                    AnglesVec = self.anglesRAD, # array of angles in radians
                    ObjSize = self.output_size, # a scalar to define the reconstructed object dimensions
                    datafidelity=self.datafidelity,# data fidelity, choose LS, PWLS
                    nonnegativity=self.nonnegativity, # enable nonnegativity constraint (set to 'on')
                    OS_number = self.ordersubsets, # the number of subsets, NONE/(or > 1) ~ classical / ordered subsets
                    tolerance = self.tolerance , # tolerance to stop outer iterations earlier
                    device='gpu')
                                        
        if (self.parameters['converg_const'] == 'power'):
            self.Lipschitz_const = self.Rectools.powermethod() # calculate Lipschitz constant
        else:
            self.Lipschitz_const = self.parameters['converg_const']
        return
    
    def nInput_datasets(self):
        return 1
    def nOutput_datasets(self):
        return 1

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
