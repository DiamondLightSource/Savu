
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
        self.pad = False
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

        if self.alg_type is '3D':
            self.slice_dim = in_pData.get_slice_dimension()

        self.geom_setup_function()

    def geom_setup_2D(self):
        in_pData = self.get_plugin_in_datasets()[0]
        cor = self.cor + self.pad_amount

        sino_shape = in_pData.get_shape()
        nCols = sino_shape[self.dim_det_cols]
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

    def geom_setup_3D(self):
        in_pData = self.get_plugin_in_datasets()[0]
        sino_shape = in_pData.get_shape()
        sino_cols = sino_shape[self.dim_det_cols] + 2*self.pad_amount

        self.proj_geom = astra.create_proj_geom('parallel3d', 1.0, 1.0,
                                                self.get_max_frames(),
                                                sino_cols, self.angles)
        self.proj_geom = astra.functions.geom_2vec(self.proj_geom)
        self.proj_geom['Vectors'][:, 3] = 6.0
        self.proj_geom['Vectors'][:, 5] = self.get_max_frames()/2.0
        # change how this is calculated
        vol_geom = astra.create_vol_geom(8, 160, 160)
        self.rec_id = self.astra_function.create('-vol', vol_geom)
        self.cfg = self.cfg_setup()
#        self.sino_transpose = (self.slice_dim, dim_det_rows, self.dim_det_cols)

#    def geom_setup_3D(self):
#        inData = self.get_in_datasets()[0]
#        sino_shape = inData.get_shape()
#        sino_cols = sino_shape[self.dim_det_cols] + 2*self.pad_amount
#
#        proj_geom = astra.create_proj_geom('parallel3d', 1.0, 1.0,
#                                           self.get_max_frames(),
#                                           sino_cols, self.angles)
#        proj_geom = astra.functions.geom_2vec(proj_geom)
#        self.vectors = proj_geom['Vectors']
#        self.vectors[:, 3] = 6.0
#        self.vectors[:, 5] = self.get_max_frames()/2.0
#        vol_geom = \
#            astra.create_vol_geom(*[self.vol_shape[i] for i in [1, 0, 2]])
#        self.rec_id = self.astra_function.create('-vol', vol_geom)
#        self.cfg = self.cfg_setup()
#        dim_det_rows = list(set([0, 1, 2]).
#                            difference({self.slice_dim, self.dim_det_cols}))[0]
#        self.sino_transpose = (self.slice_dim, dim_det_rows, self.dim_det_cols)

    def array_pad(self, ctr, nPixels):
        width = nPixels - 1.0
        alen = ctr
        blen = width - ctr
        mid = (width-1.0)/2.0
        shift = round(abs(blen-alen))
        p_low = 0 if (ctr > mid) else shift
        p_high = shift + 0 if (ctr > mid) else 0
        return int(p_low), int(p_high)

    def cfg_setup(self):
        cfg = astra.astra_dict(self.name)
        cfg['ReconstructionDataId'] = self.rec_id
        if 'CUDA' in self.name:
            cfg['option'] = {'GPUindex': self.parameters['GPU_index']}
        return cfg

    def reconstruct(self, sino, cors, angles, vol_shape):
        print sino.shape
        self.sino_transpose = (1, 0, 2)
        print "processing"
        sino = sino.transpose(self.sino_transpose)
        if self.alg_type is '2D':
            sino = np.pad(sino, ((0, 0), (self.p_low, self.p_high)),
                          mode='reflect')

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
        return 8 if "3D" in self.get_parameters()[0] else 1


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

