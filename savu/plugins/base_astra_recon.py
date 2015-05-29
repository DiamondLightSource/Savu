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
.. module:: base_astra_recon
   :platform: Unix
   :synopsis: A base for all Astra toolbox reconstruction algorithms

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.base_recon import BaseRecon

import logging

import astra

import numpy as np

import math


class BaseAstraRecon(BaseRecon):
    """
    A Plugin to perform Astra toolbox reconstruction
    
    :param center_of_rotation: Center of rotation to use for the reconstruction). Default: 86.
    """
    res = 0

    def __init__(self, name='BaseAstraRecon'):
        super(BaseAstraRecon, self).__init__(name)
    
    def get_parameters(self):
        """
        Get reconstruction_type and number_of_iterations parameters
        """
        logging.error("get_parameters needs to be implemented")
        raise NotImplementedError("get_parameters " +
                                  "needs to be implemented")

    def set_iterations(self, params):
        if params[0] == "FBP":
            iterations = 1
        else:
            iterations = params[1]
        return iterations
        

    def reconstruct(self, sinogram, centre_of_rotation, angles, shape, center):      
        ctr = centre_of_rotation
        width = sinogram.shape[1]
        pad = 50

        sino = np.nan_to_num(1./sinogram)

        # pad the array so that the centre of rotation is in the middle
        alen = ctr
        blen = width - ctr
        mid = width / 2.0

        if (ctr > mid):
            plow = pad
            phigh = (alen - blen) + pad
        else:
            plow = (blen - alen) + pad
            phigh = pad

        logdata = np.log(sino+1)
        sinogram = np.pad(logdata, ((0, 0), (int(plow), int(phigh))),
                          mode='reflect')

        width = sinogram.shape[1]

        vol_geom = astra.create_vol_geom(shape[0], shape[1])
        proj_geom = astra.create_proj_geom('parallel', 1.0, width,
                                           np.deg2rad(angles))

        sinogram_id = astra.data2d.create("-sino", proj_geom, sinogram)

        # Create a data object for the reconstruction
        rec_id = astra.data2d.create('-vol', vol_geom)

        params = self.get_parameters();
        
        cfg = astra.astra_dict(params[0])
        cfg['ReconstructionDataId'] = rec_id
        cfg['ProjectionDataId'] = sinogram_id
        
        if not "CUDA" in params[0]:
            proj_id = astra.create_projector('strip', proj_geom, vol_geom)
            cfg['ProjectorId'] = proj_id
         
        # Create the algorithm object from the configuration structure
        alg_id = astra.algorithm.create(cfg)

        iterations = int(self.set_iterations(params))
        
        # This will have a runtime in the order of 10 seconds.
        astra.algorithm.run(alg_id, iterations)
        
        if "CUDA" in params[0] and "FBP" not in params[0]:
                self.res += astra.algorithm.get_res_norm(alg_id)**2
                print math.sqrt(self.res)
        
        # Get the result
        rec = astra.data2d.get(rec_id)

        astra.algorithm.delete(alg_id)
        astra.data2d.delete(rec_id)
        astra.data2d.delete(sinogram_id)
        
        return rec
        

        