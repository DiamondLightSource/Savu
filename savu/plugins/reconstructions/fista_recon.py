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
   :synopsis: Wrapper around FISTA iterative algorithm in TomoPhantom software

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
#from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.cpu_plugin import CpuPlugin

import numpy as np
#import tomophantom
from tomophantom.supp.recModIter import RecTools

from savu.plugins.utils import register_plugin
from scipy import ndimage

@register_plugin
class FistaRecon(BaseRecon, CpuPlugin):
    """
    A Plugin to reconstruct an image by using FISTA iterative algorithm implemented \
    in TomoPhantom package. Dependencies on ASTRA toolbox and CCPi RGL toolkit: \
    https://github.com/vais-ral/CCPi-Regularisation-Toolkit.

    :param iterationsFISTA: Number of FISTA iterations. Default: 100.
    :param datafidelity: Data fidelity, Least Squares only at the moment. Default: 'LS'.
    :param converg_const: Lipschitz constant, can be set to a value. Default: 'power'.
    :param regularisation: To regularise choose ROF_TV, FGP_TV, SB_TV, LLT_ROF,\
                            TGV, NDF, DIFF4th. Default: None.
    :param regularisation_parameter: Regularisation (smoothing) value, higher \
                            the value stronger the smoothing effect. Default: 0.01.
    :param regularisation_iterations: The number of regularisation iterations. Default: 100.
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
        self.regularisation_iterations = self.parameters['regularisation_iterations']
        self.vol_shape = self.parameters['vol_shape'] # get the size of the reconstructed volume
        
        # extract data and data-related parameters
        in_data = self.get_in_datasets()[0]
        print(in_data.get_shape())
        
        in_pData = self.get_plugin_in_datasets()[0]
        
        # get the shape of the input data
        anglesTot, DetectorsDimH = in_pData.get_shape()
        #print(DetectorsDimH)
        
        # need to extract angles to initiate reconstruction class
        mData = self.get_in_meta_data()[0]
        # see all elements of the metadata
        #for attr in dir(mData):
        #    print("obj.%s = %r" % (attr, getattr(mData, attr)))
        angles = mData.get('rotation_angle').astype(np.float32)
        self.angles = np.deg2rad(angles) # get angles in radians
        
        # set parameters and initiate a TomoPhantom class object
        self.Rectools = RecTools(DetectorsDimH,  # DetectorsDimH # detector dimension (horizontal)
                    DetectorsDimV = None,  # DetectorsDimV # detector dimension (vertical) for 3D case only
                    AnglesVec = self.angles, # array of angles in radians
                    ObjSize = self.vol_shape , # a scalar to define reconstructed object dimensions
                    datafidelity='LS',# data fidelity, choose LS, PWLS (wip), GH (wip), Student (wip)
                    tolerance = 1e-06, # tolerance to stop outer iterations earlier
                    device='cpu')
        
        if (self.parameters['converg_const'] == 'power'):
            self.Lipschitz_const = self.Rectools.powermethod() # calculate Lipschitz constant
        else:
            self.Lipschitz_const = self.parameters['converg_const']
        #print(self.Lipschitz_const)
    def process_frames(self, data):
        centre_of_rotations, angles, vol_shape, init  = self.get_frame_params()
        sino = data[0].astype(np.float32)
        print(np.shape(sino))
        # sinogram = np.swapaxes(sino, 0, 1)
        #sinogram = self._shift(sino, centre_of_rotations)
        #print(np.shape(sinogram))
        #self.sino = sinogram.astype(np.float32) # get sinogram
        
        recon = np.zeros([self.vol_shape,1,self.vol_shape])
        
        # Run FISTA reconstrucion algorithm without regularisation
        #recon = self.Rectools.FISTA(sinogram, iterationsFISTA = 10, lipschitz_const = self.Lipschitz_const)
        return recon

    def get_max_frames(self):
        return 'single'