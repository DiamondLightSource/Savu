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

    def reconstruct_pre_process(self):
        self.nSinos = self.get_max_frames()
        lparams = self.get_parameters()
        self.name = lparams[0]
        self.iters = lparams[1]
        self.func_map = {'2D': self.reconstruct2D, '3D': self.reconstruct3D}

    def reconstruct(self, sinogram, centre_of_rotations, angles, vol_shape):

        sino = np.nan_to_num(1./sinogram)
        log_data = np.log(sino+1)
        p_low, p_high = self.array_pad(centre_of_rotations, sinogram.shape[1])
        sino = np.pad(log_data, ((0, 0), (p_low, p_high)), mode='reflect')

        args = [sino, angles, vol_shape]

        alg_type = '3D' if '3D' in self.name else '2D'
        rec = self.func_map[alg_type](*args)

        return rec

    def reconstruct2D(self, sino, angles, shape):

        vol_geom = astra.create_vol_geom(shape[0], shape[1])
        proj_geom = astra.create_proj_geom('parallel', 1.0, sino.shape[1],
                                           np.deg2rad(angles))
        sinogram_id = astra.data2d.create("-sino", proj_geom, sino)
        # Create a data object for the reconstruction
        rec_id = astra.data2d.create('-vol', vol_geom)

        cfg = astra.astra_dict(self.name)
        cfg['ReconstructionDataId'] = rec_id
        cfg['ProjectionDataId'] = sinogram_id

        if not "CUDA" in self.name:
            proj_id = astra.create_projector('strip', proj_geom, vol_geom)
            cfg['ProjectorId'] = proj_id

        # Create the algorithm object from the configuration structure
        alg_id = astra.algorithm.create(cfg)
        # This will have a runtime in the order of 10 seconds.
        astra.algorithm.run(alg_id, self.iters)

        if "CUDA" in self.name and "FBP" not in self.name:
                self.res += astra.algorithm.get_res_norm(alg_id)**2
                print math.sqrt(self.res)

        # Get the result
        rec = astra.data2d.get(rec_id)

        astra.algorithm.delete(alg_id)
        astra.data2d.delete(rec_id)
        astra.data2d.delete(sinogram_id)

        return rec

    def reconstruct3D(self, sino, angles, shape,):

        det_rows = sino.shape[0]
        det_cols = sino.shape[2]

        vol_geom = astra.create_vol_geom(shape[0], self.nSinos, shape[1])
        proj_geom = astra.create_proj_geom('parallel3d', 1.0, 1.0, det_cols,
                                           det_rows, np.deg2rad(angles))

        sinogram_id = astra.data3d.create("-sino", proj_geom, sino)
        # Create a data object for the reconstruction
        rec_id = astra.data3d.create('-vol', vol_geom)

        cfg = astra.astra_dict(self.name)
        cfg['ReconstructionDataId'] = rec_id
        cfg['ProjectionDataId'] = sinogram_id

        # Create the algorithm object from the configuration structure
        alg_id = astra.algorithm.create(cfg)
        # This will have a runtime in the order of 10 seconds.
        astra.algorithm.run(alg_id, self.iters)
        #if "CUDA" in params[0] and "FBP" not in params[0]:
        #self.res += astra.algorithm.get_res_norm(alg_id)**2
        #print math.sqrt(self.res)

        # Get the result
        rec = astra.data3d.get(rec_id)

        astra.algorithm.delete(alg_id)
        astra.data3d.delete(rec_id)
        astra.data3d.delete(sinogram_id)

        rec = rec[:160, :160, 1]

        return rec

    def array_pad(self, ctr, width):
        # pad the array so that the centre of rotation is in the middle
        pad = 50
        alen = ctr
        blen = width - ctr
        mid = width / 2.0

        p_low = pad if (ctr > mid) else (blen - alen) + pad
        p_high = (alen - blen) + pad if (ctr > mid) else pad
        return int(p_low), int(p_high)

    def get_max_frames(self):
        params = self.get_parameters()
        frames = 8 if "3D" in params[0] else 1
        return frames

logging.debug("Completed base_astra_recon import")
