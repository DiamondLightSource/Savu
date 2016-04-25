
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

    def reconstruct_pre_process(self):
        lparams = self.get_parameters()
        self.name = lparams[0]
        self.iters = lparams[1]
        self.alg_type = '3D' if '3D' in self.name else '2D'

        geom_func_map = {'2D': self.geom_setup_2D, '3D': self.geom_setup_3D}
        astra_func_map = {'2D': astra.data2d, '3D': astra.data3d}
        self.geom_setup_function = geom_func_map[self.alg_type]
        self.astra_function = astra_func_map[self.alg_type]

        in_pData = self.get_plugin_in_datasets()[0]
        dim_det_cols = \
            in_pData.get_data_dimension_by_axis_label('x', contains=True)

        if self.alg_type is '3D':
            self.slice_dim = in_pData.get_slice_dimension()

        self.geom_setup_function(dim_det_cols)

    def geom_setup_2D(self, dim_det_cols):
        in_pData = self.get_plugin_in_datasets()[0]
        cor = self.cor + self.pad_amount

        sino_shape = in_pData.get_shape()
        nCols = sino_shape[dim_det_cols]
        self.p_low, self.p_high = \
            self.array_pad(cor[0], nCols + 2*self.pad_amount)
        sino_width = \
            sino_shape[1] + self.p_low + self.p_high + 2*self.pad_amount

        vol_geom = astra.create_vol_geom(self.vol_shape[0], self.vol_shape[1])
        self.proj_geom = astra.create_proj_geom('parallel', 1.0, sino_width,
                                                np.deg2rad(self.angles))

        self.rec_id = self.astra_function.create('-vol', vol_geom)
        self.cfg = self.cfg_setup()
        if self.alg_type is '2D' and "CUDA" not in self.name:
            proj_id = astra.create_projector('strip', self.proj_geom, vol_geom)
            self.cfg['ProjectorId'] = proj_id

    def geom_setup_3D(self, dim_det_cols):
        pass

    def array_pad(self, ctr, width):
        pad = 1
        alen = ctr
        blen = width - ctr
        mid = width / 2.0
        p_low = pad if (ctr > mid) else (blen - alen) + pad
        p_high = (alen - blen) + pad if (ctr > mid) else pad
        return int(p_low), int(p_high)

    def cfg_setup(self):
        cfg = astra.astra_dict(self.name)
        cfg['ReconstructionDataId'] = self.rec_id
        if 'CUDA' in self.name:
            cfg['option'] = {'GPUindex': self.parameters['GPU_index']}
        return cfg

    def reconstruct(self, sino, cors, angles, vol_shape):
        sino = \
            np.pad(sino, ((0, 0), (self.p_low, self.p_high)), mode='reflect')

        sino_id = self.astra_function.create("-sino", self.proj_geom, sino)
        self.cfg['ProjectionDataId'] = sino_id
        self.alg_id = astra.algorithm.create(self.cfg)
        astra.algorithm.run(self.alg_id, self.iters)
        rec = self.astra_function.get(self.rec_id)
        astra.algorithm.delete(self.alg_id)
        self.astra_function.delete(sino_id)
        return rec

    def post_process(self):
        self.astra_function.delete(self.rec_id)

    def get_max_frames(self):
        # print self.get_parameters()[0]
        # frames = 8 if "3D" in self.get_parameters()[0] else 1
        return 1


## Add this as citation information:
## W. van Aarle, W. J. Palenstijn, J. De Beenhouwer, T. Altantzis, S. Bals,  \
## K J. Batenburg, and J. Sijbers, "The ASTRA Toolbox: A platform for advanced \
## algorithm development in electron tomography", Ultramicroscopy (2015),
## http://dx.doi.org/10.1016/j.ultramic.2015.05.002
#
## Additionally, if you use parallel beam GPU code, we would appreciate it if \
## you would refer to the following paper:
##
## W. J. Palenstijn, K J. Batenburg, and J. Sijbers, "Performance improvements
## for iterative electron tomography reconstruction using graphics processing
## units (GPUs)", Journal of Structural Biology, vol. 176, issue 2, pp. 250-253,
## 2011, http://dx.doi.org/10.1016/j.jsb.2011.07.017

