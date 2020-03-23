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
    A Plugin to reconstruct full-field tomographic projection data using state-of-the-art regularised iterative algorithms from \
    the ToMoBAR package. ToMoBAR includes FISTA and ADMM iterative methods and depends on the ASTRA toolbox and the CCPi RGL toolkit: \
    https://github.com/vais-ral/CCPi-Regularisation-Toolkit.

    :param output_size: Number of rows and columns in the \
        reconstruction. Default: 'auto'.
    :param data_fidelity: Data fidelity, chosoe Least Squares only at the moment. Default: 'LS'.
    :param data_Huber_thresh: Threshold parameter for __Huber__ data fidelity . Default: None.
    :param data_any_rings: a parameter to suppress various artifacts including rings and streaks. Default: None.
    :param data_any_rings_winsizes: half window sizes to collect background information [detector, angles, num of projections]. Default: (9,7,0).
    :param data_any_rings_power: a power parameter for Huber model. Default: 1.5.
    :param data_full_ring_GH: Regularisation variable for full constant ring removal (GH model). Default: None.
    :param data_full_ring_accelerator_GH: Acceleration constant for GH ring removal. Default: 10.0.
    :param algorithm_iterations: Number of outer iterations for FISTA (default) or ADMM methods. Default: 20.
    :param algorithm_verbose: print iterations number and other messages ('off' by default). Default: 'off'.
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
        super(TomobarRecon, self).__init__("TomobarRecon")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0] // 2) - centre_of_rotation
        result = ndimage.interpolation.shift(sinogram,
                                             (centre_of_rotation_shift, 0))
        return result

    def pre_process(self):
        # extract given parameters into dictionaries suitable for ToMoBAR input
        self._data_ = {'OS_number' : self.parameters['algorithm_ordersubsets'],
                       'huber_threshold' : self.parameters['data_Huber_thresh'],
                       'ring_weights_threshold' :  self.parameters['data_any_rings'],
                       'ring_tuple_halfsizes' :  self.parameters['data_any_rings_winsizes'],
                       'ring_huber_power' :  self.parameters['data_any_rings_power'],
                       'ringGH_lambda' :  self.parameters['data_full_ring_GH'],
                       'ringGH_accelerate' :  self.parameters['data_full_ring_accelerator_GH']}

        self._algorithm_ = {'iterations' : self.parameters['algorithm_iterations'],
			    'nonnegativity' : self.parameters['algorithm_nonnegativity'],
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
        centre_of_rotations, angles, self.vol_shape, init  = self.get_frame_params()
        sinogram = data[0].astype(np.float32)
        anglesTot, self.DetectorsDimH = np.shape(sinogram)
        self.anglesRAD = np.deg2rad(angles.astype(np.float32))
        self._data_.update({'projection_norm_data' : sinogram})
        """
        # if one selects PWLS model and provides raw input data
        if (self.parameters['data_fidelity'] == 'PWLS'):
        rawdata = data[1].astype(np.float32)
        rawdata /= np.max(rawdata)
        self._data_.update({'projection_raw_data' : rawdata})
        """

        # set parameters and initiate the ToMoBAR class object
        self.Rectools = RecToolsIR(DetectorsDimH = self.DetectorsDimH,  # DetectorsDimH # detector dimension (horizontal)
                    DetectorsDimV = None,  # DetectorsDimV # detector dimension (vertical) for 3D case only
                    CenterRotOffset = None, # Center of Rotation (CoR) scalar (for 3D case only)
                    AnglesVec = self.anglesRAD, # array of angles in radians
                    ObjSize = self.vol_shape[0] , # a scalar to define the reconstructed object dimensions
                    datafidelity=self.parameters['data_fidelity'],# data fidelity, choose LS, PWLS
                    device_projector='gpu')

        # Run FISTA reconstrucion algorithm here
        recon = self.Rectools.FISTA(self._data_, self._algorithm_, self._regularisation_)
        return recon

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
