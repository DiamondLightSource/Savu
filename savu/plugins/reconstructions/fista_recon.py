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
.. module:: fista_recon
   :platform: Unix
   :synopsis: Wrapper around FISTA iterative algorithm in FISTA-tomo

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.gpu_plugin import GpuPlugin

import numpy as np
# install FISTA-tomo with: conda install -c dkazanc fista-tomo
# or from https://github.com/dkazanc/FISTA-tomo
from fista.tomo.recModIter import RecTools

from savu.plugins.utils import register_plugin
from scipy import ndimage

@register_plugin
class FistaRecon(BaseRecon, GpuPlugin):
    """
    A Plugin to reconstruct data by using FISTA iterative algorithm implemented \
    in FISTA-tomo package. Dependencies on FISTA-tomo, ASTRA toolbox and CCPi RGL toolkit: \
    https://github.com/vais-ral/CCPi-Regularisation-Toolkit.

    :param iterationsFISTA: Number of FISTA iterations. Default: 250.
    :param datafidelity: Data fidelity, Least Squares only at the moment. Default: 'LS'.
    :param converg_const: Lipschitz constant, can be set to a value. Default: 'power'.
    :param regularisation: To regularise choose ROF_TV, FGP_TV, SB_TV, LLT_ROF,\
                            TGV, NDF, DIFF4th. Default: 'SB_TV'.
    :param regularisation_parameter: Regularisation (smoothing) value, higher \
                            the value stronger the smoothing effect. Default: 0.01.
    :param regularisation_iterations: The number of regularisation iterations. Default: 50.
    :param time_marching_parameter: Time marching parameter, relevant for \
                    (ROF_TV, LLT_ROF, NDF, DIFF4th) penalties. Default: 0.0025.
    :param edge_param: Edge (noise) related parameter, relevant for NDF and DIFF4th. Default: 0.01.
    :param NDF_penalty: NDF specific penalty type: 1 - Huber, 2 - Perona-Malik, 3 - Tukey Biweight. Default: 1.
    :param regularisation_parameter2:  Regularisation (smoothing) value for LLT_ROF method. Default: 0.005.
    """

    def __init__(self):
        super(FistaRecon, self).__init__("FistaRecon")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0]/2) - \
            float(centre_of_rotation)
        return ndimage.interpolation.shift(sinogram, centre_of_rotation_shift)
    
    def pre_process(self):
        # extract given parameters
        self.iterationsFISTA = self.parameters['iterationsFISTA']
        self.datafidelity = self.parameters['datafidelity']
        self.converg_const = self.parameters['converg_const']
        self.regularisation = self.parameters['regularisation']
        self.regularisation_parameter = self.parameters['regularisation_parameter']
        self.regularisation_parameter2 = self.parameters['regularisation_parameter2']
        self.regularisation_iterations = self.parameters['regularisation_iterations']
        self.time_marching_parameter = self.parameters['time_marching_parameter']
        self.edge_param = self.parameters['edge_param']
        self.NDF_penalty = self.parameters['NDF_penalty']
        self.Rectools = None

        # extract data and data-related parameters
        # in_data = self.get_in_datasets()[0]
        # print(in_data.get_shape())
        
        #in_pData = self.get_plugin_in_datasets()[0]
        
        # get the shape of the input data
        #anglesTot, DetectorsDimH = in_pData.get_shape()
        
        # need to extract angles to initiate reconstruction class
        # mData = self.get_in_meta_data()[0]
        # see all elements of the metadata
        #for attr in dir(mData):
        #    print("obj.%s = %r" % (attr, getattr(mData, attr)))
        # angles = mData.get('rotation_angle').astype(np.float32)
        # self.angles = np.deg2rad(angles) # get angles in radians

        #print(self.Lipschitz_const)
    def process_frames(self, data):
        centre_of_rotations, angles, self.vol_shape, init  = self.get_frame_params()
        sino = data[0].astype(np.float32)
        anglesTot, self.DetectorsDimH = np.shape(sino)
        self.angles = np.deg2rad(angles.astype(np.float32))
        
        # check if the reconstruction class has been initialised and calculate Lipschitz const
        self.get_value() 
        # recon = np.zeros([self.vol_shape,1,self.vol_shape])
        
        # Run FISTA reconstrucion algorithm
        recon = self.Rectools.FISTA(sino,\
                                    iterationsFISTA = self.iterationsFISTA,\
                                    regularisation = self.regularisation,\
                                    regularisation_parameter = self.regularisation_parameter,\
                                    regularisation_iterations = self.regularisation_iterations,\
                                    regularisation_parameter2 = self.regularisation_parameter2,\
                                    time_marching_parameter = self.time_marching_parameter,\
                                    edge_param = self.edge_param,\
                                    NDF_penalty = self.NDF_penalty,\
                                    lipschitz_const = self.Lipschitz_const)
        return recon

    def get_value(self):
        if self.Rectools is not None:
            return 
        
       # set parameters and initiate a TomoPhantom class object
        self.Rectools = RecTools(DetectorsDimH = self.DetectorsDimH,  # DetectorsDimH # detector dimension (horizontal)
                    DetectorsDimV = None,  # DetectorsDimV # detector dimension (vertical) for 3D case only
                    AnglesVec = self.angles, # array of angles in radians
                    ObjSize = self.vol_shape[0] , # a scalar to define reconstructed object dimensions
                    datafidelity=self.datafidelity,# data fidelity, choose LS, PWLS (wip), GH (wip), Student (wip)
                    tolerance = 1e-06, # tolerance to stop outer iterations earlier
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