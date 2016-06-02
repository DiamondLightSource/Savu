
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
import math

from savu.plugins.base_recon import BaseRecon


class NewBaseAstraRecon(BaseRecon):
    """
    A Plugin to perform Astra toolbox reconstruction

    :param init_vol: Dataset to use as volume initialiser. Default: None.
    :param FBP_filter: The FBP reconstruction filter type (none|ram-lak|\
        shepp-logan|cosine|hamming|hann|tukey|lanczos|triangular|gaussian|\
        barlett-hann|blackman|nuttall|blackman-harris|blackman-nuttall|\
        flat-top|kaiser|parzen). Default: 'ram-lak'.
    """

    def __init__(self, name='NewBaseAstraRecon'):
        super(NewBaseAstraRecon, self).__init__(name)
        self.res = 0

    def get_parameters(self):
        """
        Get reconstruction_type and number_of_iterations parameters
        """
        logging.error("get_parameters needs to be implemented")
        raise NotImplementedError("get_parameters needs to be implemented")

    def pre_process(self):
        # *****check here if there are deviations in the cor and determine the algorithm***
        # perhaps do the above in base pre-process
        self.alg, self.iters = self.get_parameters()
        if '3D' in self.alg:
            self.setup_3D()
            self.reconstruct = self.astra_3D_recon
        else:
            self.setup_2D()
            self.reconstruct = self.astra_2D_recon

    def reconstruct(self, sino, cors, angles, vol_shape):
        self.reconstruct(sino, cors, angles, vol_shape)

    def setup_2D(self):
        pData = self.get_plugin_in_datasets()[0]
        detX = pData.get_data_dimension_by_axis_label('x', contains=True)
        self.sino_shape = pData.get_shape()
        self.nDims = len(self.sino_shape)
        self.dim_detX = detX if self.nDims is 2 else detX-1
        self.nCols = self.sino_shape[detX]
        self.slice_dir = pData.get_slice_dimension()
        self.nSinos = self.sino_shape[self.slice_dir] if self.nDims is 3 else 1
        self.slice_func = self.slice_sino(self.nDims)
        self.out_shape = self.get_plugin_out_datasets()[0].shape

    def slice_sino(self, nDims):
        if nDims is 2:
            return lambda x, sslice: np.expand_dims(x, axis=self.slice_dir)[sslice]
        else:
            return lambda x, sslice: x[sslice]

    def astra_2D_recon(self, sino, cors, angles, vol_shape, init=None):
        sslice = [slice(None)]*self.nDims
        recon = np.zeros(self.out_shape)
        if self.nDims is 2:
            recon = np.expand_dims(recon, axis=self.slice_dir)

        # create volume geom
        vol_geom = astra.create_vol_geom(*vol_shape[0:1])

        for i in range(self.nSinos):
            sslice[self.slice_dir] = i
            try:
                cor = cors[i]
            except:
                cor = cors[0]

            pad_sino = self.pad_sino(self.slice_func(sino, sslice), cor)

            # create projection geom
            proj_geom = astra.create_proj_geom('parallel', 1.0,
                                               pad_sino.shape[self.dim_detX],
                                               np.deg2rad(self.angles))
            # create sinogram id
            sino_id = astra.data2d.create("-sino", proj_geom, pad_sino)

            # create reconstruction id
            if init is not None:
                print "initialising the volume to init"
                rec_id = astra.data2d.create('-vol', vol_geom, init)
            else:
                rec_id = astra.data2d.create('-vol', vol_geom)

            # setup configuration options
            cfg = astra.astra_dict(self.alg)
            cfg['ReconstructionDataId'] = rec_id
            cfg['ProjectionDataId'] = sino_id
            cfg['FilterType'] = self.parameters['FBP_filter']
            if 'projector' in self.parameters.keys():
                cfg['ProjectorId'] = astra.create_projector(
                    self.parameters['projector'], proj_geom, vol_geom)
            cfg = self.set_options(cfg)

            # create algorithm id
            alg_id = astra.algorithm.create(cfg)

            # run algorithm
            astra.algorithm.run(alg_id,
                                self.parameters['number_of_iterations'])
            # get reconstruction matrix
            recon[sslice] = astra.data2d.get(rec_id)

            # delete geometry
            astra.algorithm.delete(alg_id)
            astra.data2d.delete(sino_id)
            astra.data2d.delete(rec_id)
        return recon

    def astra_3D_recon(self, sino, cors, angles, vol_shape):
        pass

    def pad_sino(self, sino, cor):
        centre_pad = self.array_pad(cor, self.nCols)
        sino_width = sino.shape[self.dim_detX]
        new_width = sino_width + max(centre_pad)
        sino_pad = \
            int(math.ceil(float(sino_width)/new_width * self.sino_pad)/2)
        pad = np.array([sino_pad]*2) + centre_pad
        pad_tuples = [(0, 0)]*(len(sino.shape)-1)
        pad_tuples.insert(self.pad_dim, tuple(pad))
        return np.pad(sino, tuple(pad_tuples), mode='edge')

    def array_pad(self, ctr, nPixels):
        width = nPixels - 1.0
        alen = ctr
        blen = width - ctr
        mid = (width-1.0)/2.0
        shift = round(abs(blen-alen))
        p_low = 0 if (ctr > mid) else shift
        p_high = shift + 0 if (ctr > mid) else 0
        return np.array([int(p_low), int(p_high)])

    def setup(self):
        self.astra_setup()
        if self.parameters['init_vol']:
            self.parameters['in_datasets'].append(self.parameters['init_vol'])
            self._set_plugin_datasets()
        super(NewBaseAstraRecon, self).setup()

    def get_max_frames(self):
        #return 8 if "3D" in self.get_parameters()[0] else 1
        return 20

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

