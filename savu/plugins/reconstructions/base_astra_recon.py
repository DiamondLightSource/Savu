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
.. module:: old_base_astra_recon
   :platform: Unix
   :synopsis: A base for all Astra toolbox reconstruction algorithms

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging
import astra
import numpy as np

from savu.plugins.base_recon import BaseRecon


class BaseAstraRecon(BaseRecon):
    """
    A Plugin to perform Astra toolbox reconstruction
    level
    :param center_of_rotation: Center of rotation to use for the \
        reconstruction). Default: 0.
    """

    def __init__(self, name='BaseAstraRecon'):
        super(BaseAstraRecon, self).__init__(name)
        self.res = 0

    def get_parameters(self):
        """
        Get reconstruction_type and number_of_iterations parameters
        """
        logging.error("get_parameters needs to be implemented")
        raise NotImplementedError("get_parameters needs to be implemented")

    def pre_process(self):
        lparams = self.get_parameters()
        self.name = lparams[0]
        self.iters = lparams[1]
        self.alg_type = '3D' if '3D' in self.name else '2D'

        geom_func_map = {'2D': self.geom_setup_2D, '3D': self.geom_setup_3D}
        astra_func_map = {'2D': astra.data2d, '3D': astra.data3d}
        self.geom_setup_function = geom_func_map[self.alg_type]
        self.astra_function = astra_func_map[self.alg_type]

        in_pData = self.get_plugin_in_datasets()[0]
        self.dim_det_cols = \
            in_pData.get_data_dimension_by_axis_label('x', contains=True)
        self.dim_rot = \
            in_pData.get_data_dimension_by_axis_label('rotation_angle')
        if self.alg_type is '3D':
            self.slice_dim = in_pData.get_slice_dimension()

    def reconstruct(self, sino, cors, angles, vol_shape):
        self.nCols = sino.shape[self.dim_det_cols]
        self.nAngles = sino.shape[self.dim_rot]
        sino, vol_geom, proj_geom = \
            self.geom_setup_function(sino, angles, vol_shape, cors)
        rec = self.astra_reconstruction(sino, vol_geom, proj_geom)
        self.astra_delete()
        return rec

    def astra_reconstruction(self, sino, vol_geom, proj_geom):
        # currently hard-coded - for 3D version only!
        # sino = np.transpose(sino, (1, 0, 2))
        self.sino_id = self.astra_function.create("-sino", proj_geom, sino)
        # Create a data object for the reconstruction
        self.rec_id = self.astra_function.create('-vol', vol_geom)
        cfg = self.cfg_setup()
        if self.alg_type is '2D' and "CUDA" not in self.name:
            proj_id = astra.create_projector('strip', proj_geom, vol_geom)
            cfg['ProjectorId'] = proj_id
        return self.run_astra(cfg)

    def run_astra(self, cfg):
        # Create the algorithm object from the configuration structure
        self.alg_id = astra.algorithm.create(cfg)
        # This will have a runtime in the order of 10 seconds.
        astra.algorithm.run(self.alg_id, self.iters)
#
#        if "CUDA" in self.name and "FBP" not in self.name:
#            self.res += astra.algorithm.get_res_norm(self.alg_id)**2
#            print math.sqrt(self.res)
        temp = self.astra_function.get(self.rec_id)
        return temp

    def geom_setup_2D(self, sino, angles, shape, cors):
        p_low, p_high = self.array_pad(cors, self.nCols)
        sino = np.pad(sino, ((0, 0), (p_low, p_high)), mode='reflect')
        vol_geom = astra.create_vol_geom(shape[0], shape[1])
        proj_geom = astra.create_proj_geom('parallel', 1.0, sino.shape[1],
                                           np.deg2rad(angles))
        return sino, vol_geom, proj_geom

    def geom_setup_3D(self, sino, angles, shape, cors):
        nSinos = sino.shape[self.slice_dim]
        length = len(angles)
        angles = np.deg2rad(angles)

        vectors = np.zeros((length, 12))
        for i in range(len(angles)):
            # ray direction
            vectors[i, 0] = np.sin(angles[i])
            vectors[i, 1] = -np.cos(angles[i])
            vectors[i, 2] = 0

            # center of detector
            vectors[i, 3:6] = 0

            # vector from detector pixel (0,0) to (0,1)
            vectors[i, 6] = np.cos(angles[i])
            vectors[i, 7] = np.sin(angles[i])
            vectors[i, 8] = 0

            # vector from detector pixel (0,0) to (1,0)
            vectors[i, 9] = 0
            vectors[i, 10] = 0
            vectors[i, 11] = 1

#        i = range(length)
#        # ray direction
#        vectors[i, 0] = np.sin(theta[i])
#        vectors[i, 1] = -np.cos(theta[i])
#        vectors[i, 2] = 0
#        # detector centre (use this for translation)
#        # assuming all sinograms are translated by the same amount for now
#        #det_vec = [cors[0], 0, 0]
#        det_vec = [0, 0, 0]
#        vectors[i, 3:6] = det_vec
#        # (use the following vectors for rotation)
#        # vector from detector pixel (0,0) to (0,1)
#        vectors[i, 6] = np.cos(theta[i])
#        vectors[i, 7] = np.sin(theta[i])
#        vectors[i, 8] = 0
#        # vector from detector pixel (0,0) to (1,0)
#        vectors[i, 9:12] = [0, 0, 1]

        # Parameters: #rows, #columns, vectors
        vol_geom = astra.create_vol_geom(nSinos, shape[0], shape[2])
        proj_geom = astra.create_proj_geom('parallel3d_vec', sino.shape[1],
                                           sino.shape[2], vectors)
        return vol_geom, proj_geom

    def astra_delete(self):
        astra.algorithm.delete(self.alg_id)
        self.astra_function.delete(self.rec_id)
        self.astra_function.delete(self.sino_id)

    def cfg_setup(self):
        cfg = astra.astra_dict(self.name)
        cfg['ReconstructionDataId'] = self.rec_id
        cfg['ProjectionDataId'] = self.sino_id
        if 'CUDA' in self.name:
            cfg['option'] = {'GPUindex': self.parameters['GPU_index']}
        return cfg

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
        #print self.get_parameters()[0]
        frames = 8 if "3D" in self.get_parameters()[0] else 1
        return frames


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
