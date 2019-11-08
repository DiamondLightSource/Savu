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
   for advanced iterative image reconstruction

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.gpu_plugin import GpuPlugin

import numpy as np
from tomobar.methodsIR import RecToolsIR

from savu.plugins.utils import register_plugin
from scipy import ndimage

@register_plugin
class TomobarRecon(BaseRecon, GpuPlugin):
    """
---
      - name: TomobarRecon
        category: Reconstructor
        synopsis: A wrapper around TOmographic MOdel-BAsed Reconstruction (ToMoBAR) software for advanced iterative image reconstruction.
        verbose: A plugin to reconstruct full-field tomographic projection data using state-of-the-art regularised iterative algorithms from the ToMoBAR package. ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA toolbox and the CCPi RGL toolkit
        parameters:
           - output_size:
                  visibility: user
                  type: str
                  description: Number of rows and columns in the reconstruction.
                  default: auto
           - iterations:
                  visibility: user
                  type: int
                  description: Number of outer iterations for FISTA (default) or ADMM methods.
                  default: 20
           - datafidelity:
                  visibility: user
                  type: str
                  description: Least Squares only at the moment.
                  default: LS
           - nonnegativity:
                  visibility: user
                  type: str
                  options: [Enable, None]
                  description: Non negativity constraint, choose Enable or None.
                  default: Enable
           - ordersubsets:
                  visibility: user
                  type: int
                  description: The number of ordered-subsets to accelerate reconstruction.
                  default: 6
           - converg_const:
                  visibility: user
                  type: str
                  description: Lipschitz constant, can be set to a value or automatic calculation.
                  default: power
           - method:
                  visibility: user
                  type: str
                  options: [ROF_TV, FGP_TV, SB_TV, NLTV, TGV, LLT_ROF, NDF, Diff4th]
                  description:
                    summary: The denoising method - This is a short description
                    verbose: To regularise choose methods ROF_TV, FGP_TV, SB_TV, LLT_ROF, NDF, Diff4th.
                    options:
                        ROF_TV: Rudin-Osher-Fatemi Total Variation model
                        FGP_TV: Fast Gradient Projection Total Variation model
                        SB_TV: Split Bregman Total Variation model
                        NLTV: Nonlocal Total Variation model
                        TGV: Total Generalised Variation model
                        LLT_ROF: Lysaker, Lundervold and Tai model combined with Rudin-Osher-Fatemi
                        NDF: Nonlinear/Linear Diffusion model (Perona-Malik, Huber or Tukey)
                        DIFF4th: Fourth-order nonlinear diffusion model
                  default: FGP_TV
           - reg_par:
                  visibility: user
                  type: float
                  description:
                    summary: Regularisation parameter. The higher the value, the stronger the smoothing effect
                    range: Recommended between 0 and 1
                  default: 0.0001
           - max_iterations:
                  visibility: user
                  type: int
                  description: Total number of regularisation iterations
                  default: 350
                  dependency:
                  method:
                    ROF_TV: 1000
                    FGP_TV: 500
                    SB_TV: 100
                    NLTV: 3
                    TGV: 1000
                    LLT_ROF: 1000
                    NDF: 1000
                    DIFF4th: 1000
           - time_step:
                  visibility: user
                  type: float
                  dependency:
                    method: [ROF_TV, LLT_ROF, NDF, Diff4th]
                  description:
                    summary: Time marching step
                    range: Recommended between 0.0001 and 0.001
                  default: 0.001
           - edge_param:
                  visibility: user
                  type: float
                  dependency:
                    method: [NDF, Diff4th]
                  description:
                    summary: Edge (noise) related parameter
                    range:
                  default: 0.01
           - regularisation_parameter2:
                  visibility: user
                  type: float
                  dependency:
                    method: LLT_ROF
                  description:
                    summary: Regularisation (smoothing) value
                    range:
                  default: 0.005
           - NDF_penalty:
                  visibility: user
                  type: str
                  options: [Huber, Perona, Tukey]
                  description:
                    summary: Penalty type
                    verbose: Nonlinear/Linear Diffusion model (NDF) specific penalty type.
                    options:
                      Huber: Huber
                      Perona: Perona-Malik model
                      Tukey: Tukey
                  dependency:
                    method: NDF
                  default: Huber
           - tolerance:
                  visibility: user
                  type: float
                  description:
                    summary: Tolerance to stop outer iterations earlier.
                    range:
                  default: 5e-10
           - ring_variable:
                  visibility: user
                  type: float
                  dependency:
                    method: LLT_ROF
                  description:
                    summary: Regularisation variable for ring removal
                    range:
                  default: 0.0
           - ring_accelerator:
                  visibility: user
                  type: float
                  description:
                    summary: Acceleration constant for ring removal (use with care)
                    range:
                  default: 50.0
    """

    '''
                  
    A Plugin to reconstruct full-field tomographic projection data using state-of-the-art regularised iterative algorithms from \
    the ToMoBAR package. ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA toolbox and the CCPi RGL toolkit: \
    https://github.com/vais-ral/CCPi-Regularisation-Toolkit.

    :param output_size: Number of rows and columns in the \
        reconstruction. Default: 'auto'.
    :param iterations: Number of outer iterations for FISTA (default) or ADMM methods. Default: 20.
    :param datafidelity: Data fidelity, Least Squares only at the moment. Default: 'LS'.
    :param nonnegativity: Nonnegativity constraint, choose Enable or None. Default: 'ENABLE'.
    :param ordersubsets: The number of ordered-subsets to accelerate reconstruction. Default: 6.
    :param converg_const: Lipschitz constant, can be set to a value or automatic calculation. Default: 'power'.
    :param regularisation: To regularise choose methods ROF_TV, FGP_TV, SB_TV, LLT_ROF,\
                             NDF, Diff4th. Default: 'FGP_TV'.
    :param regularisation_parameter: Regularisation (smoothing) value, higher \
                            the value stronger the smoothing effect. Default: 0.0001.
    :param regularisation_iterations: The number of regularisation iterations. Default: 350.
    :param time_marching_parameter: Time marching parameter, relevant for \
                    (ROF_TV, LLT_ROF, NDF, Diff4th) penalties. Default: 0.0025.
    :param edge_param: Edge (noise) related parameter, relevant for NDF and Diff4th. Default: 0.01.
    :param regularisation_parameter2:  Regularisation (smoothing) value for LLT_ROF method. Default: 0.005.
    :param NDF_penalty: NDF specific penalty type Huber, Perona, Tukey. Default: 'Huber'.
    :param tolerance: Tolerance to stop outer iterations earlier. Default: 5e-10.
    :param ring_variable: Regularisation variable for ring removal. Default: 0.0.
    :param ring_accelerator: Acceleration constant for ring removal (use with care). Default: 50.0.
    '''

    def __init__(self):
        super(TomobarRecon, self).__init__("TomobarRecon")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0]/2) - centre_of_rotation
        result = ndimage.interpolation.shift(sinogram,
                                             (centre_of_rotation_shift, 0))
        return result
    
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
        self.output_size = self.parameters['output_size']
        self.tolerance = self.parameters['tolerance']
        
        
        self.RecToolsIR = None
        if (self.ordersubsets > 1):
            self.regularisation_iterations = (int)(self.parameters['regularisation_iterations']/self.ordersubsets) + 1
        else:
            self.regularisation_iterations = self.parameters['regularisation_iterations']

    def process_frames(self, data):
        centre_of_rotations, angles, self.vol_shape, init  = self.get_frame_params()
        sino = data[0].astype(np.float32)
        anglesTot, self.DetectorsDimH = np.shape(sino)
        self.anglesRAD = np.deg2rad(angles.astype(np.float32))
       
        # check if the reconstruction class has been initialised and calculate 
        # Lipschitz constant if not given explicitly
        self.setup_Lipschitz_constant()

        # Run FISTA reconstrucion algorithm here
        # Fast Iterative Shrinking Thresholding Algorithm
        recon = self.Rectools.FISTA(sino,\
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
        return recon

    def setup_Lipschitz_constant(self):
        if self.RecToolsIR is not None:
            return 
        
       # set parameters and initiate a TomoBar class object
        self.Rectools = RecToolsIR(DetectorsDimH = self.DetectorsDimH,  # DetectorsDimH # detector dimension (horizontal)
                    DetectorsDimV = None,  # DetectorsDimV # detector dimension (vertical) for 3D case only
                    CenterRotOffset = None, # Center of Rotation (CoR) scalar (for 3D case only)
                    AnglesVec = self.anglesRAD, # array of angles in radians
                    ObjSize = self.vol_shape[0] , # a scalar to define the reconstructed object dimensions
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
