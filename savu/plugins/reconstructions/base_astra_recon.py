# -*- coding: utf-8 -*-
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
import logging
#import time
#from mpi4py import MPI

logging.debug("Importing packages in base_astra_recon")

from savu.plugins.base_recon import BaseRecon

#rank = 0
#my_rank = MPI.COMM_WORLD.rank
#processes = MPI.COMM_WORLD.size
#MPI.COMM_WORLD.Barrier()
#while (rank < processes):
#    if (my_rank == rank):
#        logging.info("***************rank %s, size %s", my_rank, processes)
#        logging.info("Imported astra")
#        time.sleep(5)
#        import astra
#        logging.info("Astra imported")
#    rank += 1
#    MPI.COMM_WORLD.Barrier()

logging.debug("Imported astra")
import astra

import numpy as np
logging.debug("Imported numpy")

import math
logging.debug("Imported math")


class BaseAstraRecon(BaseRecon):
    """
    A Plugin to perform Astra toolbox reconstruction
    level
    :param center_of_rotation: Center of rotation to use for the reconstruction). Default: 86.
    """

    def __init__(self, name='BaseAstraRecon'):
        super(BaseAstraRecon, self).__init__(name)
        self.res = 0

    def get_parameters(self):
        """
        Get reconstruction_type and number_of_iterations parameters
        """
        logging.error("get_parameters needs to be implemented")
        raise NotImplementedError("get_parameters " +
                                  "needs to be implemented")

    def reconstruct_pre_process(self):
        self.nSinos = self.get_max_frames()
        lparams = self.get_parameters()
        self.name = lparams[0]
        self.iters = lparams[1]

        geom_func_map = {'2D': self.geom_setup_2D, '3D': self.geom_setup_3D}
        astra_func_map = {'2D': astra.data2d, '3D': astra.data3d}
        alg_type = '3D' if '3D' in self.name else '2D'
        self.geom_setup_function = geom_func_map[alg_type]
        self.astra_function = astra_func_map[alg_type]

    def reconstruct(self, sinogram, centre_of_rotations, angles, vol_shape):
        p_low, p_high = self.array_pad(centre_of_rotations, sinogram.shape[1])
        
        # this only works in sino is 2D
        sino = np.pad(sinogram, ((0, 0), (p_low, p_high)), mode='reflect')
        vol_geom, proj_geom = self.geom_setup_function(sino, angles, vol_shape)
        return self.astra_reconstruction(sino, vol_geom, proj_geom)

    def astra_reconstruction(self, sino, vol_geom, proj_geom):
        self.sino_id = self.astra_function.create("-sino", proj_geom, sino)
        # Create a data object for the reconstruction
        self.rec_id = self.astra_function.create('-vol', vol_geom)
        cfg = self.cfg_setup()
        if not '3D' in self.name and not "CUDA" in self.name:
            proj_id = astra.create_projector('strip', proj_geom, vol_geom)
            cfg['ProjectorId'] = proj_id
        return self.run_astra(cfg)

    def run_astra(self, cfg):
        # Create the algorithm object from the configuration structure
        self.alg_id = astra.algorithm.create(cfg)
        # This will have a runtime in the order of 10 seconds.
        astra.algorithm.run(self.alg_id, self.iters)

        if "CUDA" in self.name and "FBP" not in self.name:
            self.res += astra.algorithm.get_res_norm(self.alg_id)**2
            print math.sqrt(self.res)
        return self.astra_function.get(self.rec_id)

    def geom_setup_2D(self, sino, angles, shape):
        vol_geom = astra.create_vol_geom(shape[0], shape[1])
        proj_geom = astra.create_proj_geom('parallel', 1.0, sino.shape[1],
                                           np.deg2rad(angles))
        return vol_geom, proj_geom

    def geom_setup_3D(self, sino, angles, shape):
        det_rows = sino.shape[0]
        det_cols = sino.shape[2]
        vol_geom = astra.create_vol_geom(shape[0], self.nSinos, shape[1])
        proj_geom = astra.create_proj_geom('parallel3d', 1.0, 1.0, det_cols,
                                           det_rows, np.deg2rad(angles))
        return vol_geom, proj_geom

    def astra_delete(self):
        astra.algorithm.delete(self.alg_id)
        self.astra_function.delete(self.rec_id)
        self.astra_function.delete(self.sino_id)

    def cfg_setup(self):
        cfg = astra.astra_dict(self.name)
        cfg['ReconstructionDataId'] = self.rec_id
        cfg['ProjectionDataId'] = self.sino_id
        return cfg

    def array_pad(self, ctr, width):
        # pad the array so that the centre of rotation is in the middle
        pad = 50
        alen = ctr
        blen = width - ctr
        mid = width / 2.0
        
        print "centre = ", ctr

        p_low = pad if (ctr > mid) else (blen - alen) + pad
        p_high = (alen - blen) + pad if (ctr > mid) else pad
        return int(p_low), int(p_high)

    def get_max_frames(self):
        params = self.get_parameters()
        frames = 8 if "3D" in params[0] else 1
        return frames

logging.debug("Completed base_astra_recon import")

# Add this as citation information:
# W. van Aarle, W. J. Palenstijn, J. De Beenhouwer, T. Altantzis, S. Bals,  \
# K J. Batenburg, and J. Sijbers, "The ASTRA Toolbox: A platform for advanced \
# algorithm development in electron tomography", Ultramicroscopy (2015),
# http://dx.doi.org/10.1016/j.ultramic.2015.05.002

# Additionally, if you use parallel beam GPU code, we would appreciate it if \
# you would refer to the following paper:
#
# W. J. Palenstijn, K J. Batenburg, and J. Sijbers, "Performance improvements
# for iterative electron tomography reconstruction using graphics processing
# units (GPUs)", Journal of Structural Biology, vol. 176, issue 2, pp. 250-253,
# 2011, http://dx.doi.org/10.1016/j.jsb.2011.07.017
