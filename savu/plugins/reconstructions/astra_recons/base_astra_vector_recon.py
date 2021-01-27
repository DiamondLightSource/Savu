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
.. module:: base_astra_vector_recon
   :platform: Unix
   :synopsis: A base for Astra toolbox reconstruction algorithms using vector geometry
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>
"""

import astra
import numpy as np

from savu.plugins.reconstructions.base_recon import BaseRecon

class BaseAstraVectorRecon(BaseRecon):
    """
    A Plugin to perform Astra toolbox reconstruction using vector geometry

    :u*param n_iterations: Number of Iterations - only valid for iterative \
        algorithms. Default: 1.
    """

    def __init__(self, name='BaseAstraVectorRecon'):
        super(BaseAstraVectorRecon, self).__init__(name)
        self.res = False

    def setup(self):
        self.alg = self.parameters['algorithm']
        self.get_max_frames = \
            self._get_multiple if '3D' in self.alg else self._get_single

        super(BaseAstraVectorRecon, self).setup()
        out_dataset = self.get_out_datasets()

        # if res_norm is required then setup another output dataset
        if len(out_dataset) is 2:
            self.res = True
            out_pData = self.get_plugin_out_datasets()
            in_data = self.get_in_datasets()[0]
            dim_detX = \
                in_data.get_data_dimension_by_axis_label('y', contains=True)

            nIts = self.parameters['n_iterations']
            nIts = nIts if isinstance(nIts, list) else [nIts]
            self.len_res = max(nIts)
            shape = (in_data.get_shape()[dim_detX], max(nIts))

            label = ['vol_y.voxel', 'iteration.number']
            pattern = {'name': 'SINOGRAM', 'slice_dims': (0,),
                       'core_dims': (1,)}

            out_dataset[1].create_dataset(axis_labels=label, shape=shape)
            out_dataset[1].add_pattern(pattern['name'],
                                       slice_dims=pattern['slice_dims'],
                                       core_dims=pattern['core_dims'])
            out_pData[1].plugin_data_setup(
                    pattern['name'], self.get_max_frames())

    def pre_process(self):
        self.alg = self.parameters['algorithm']
        self.iters = self.parameters['n_iterations']

        if '3D' in self.alg:
            self.setup_3D()
            self.process_frames = self.astra_3D_vector_recon
        else:
            self.setup_2D()
            self.process_frames = self.astra_2D_vector_recon

    def setup_2D(self):
        pData = self.get_plugin_in_datasets()[0]
        self.dim_detX = \
            pData.get_data_dimension_by_axis_label('x', contains=True)
        self.dim_rot = \
            pData.get_data_dimension_by_axis_label('rot', contains=True)

        self.sino_shape = pData.get_shape()
        self.nDims = len(self.sino_shape)
        self.nCols = self.sino_shape[self.dim_detX]
        self.set_mask(self.sino_shape)

    def setup_3D(self):
        pData = self.get_plugin_in_datasets()[0]
        self.sino_dim_detX = \
            pData.get_data_dimension_by_axis_label('x', contains=True)
        self.sino_dim_detY = \
            pData.get_data_dimension_by_axis_label('y', contains=True)
        self.det_rot = \
            pData.get_data_dimension_by_axis_label('angle', contains=True)
        self.sino_shape = pData.get_shape()
        self.nDims = len(self.sino_shape)
        #self.nCols = self.sino_shape[self.sino_dim_detX]
        self.slice_dir = pData.get_slice_dimension()
        #self.slice_func = self.slice_sino(self.nDims)
        """
        l = self.sino_shape[self.sino_dim_detX]
        c = np.linspace(-l/2.0, l/2.0, l)
        x, y = np.meshgrid(c, c)
        self.mask_id = False
        mask = np.array((x**2 + y**2 < (l/2.0)**2), dtype=np.float)
        self.mask = np.transpose(
            np.tile(mask, (self.get_max_frames(), 1, 1)), (1, 0, 2))
        self.manual_mask = True if not self.parameters['sino_pad'] else False
        """

    def set_mask(self, shape):
        l = self.get_plugin_out_datasets()[0].get_shape()[0]
        c = np.linspace(-l/2.0, l/2.0, l)
        x, y = np.meshgrid(c, c)
        r = (shape[self.dim_detX]-1)*self.parameters['ratio']

        outer_pad = True if self.parameters['outer_pad'] and self.padding_alg\
            else False
        if not outer_pad:
            self.manual_mask = \
                np.array((x**2 + y**2 < (r/2.0)**2), dtype=np.float)
            self.manual_mask[self.manual_mask == 0] = np.nan
        else:
            self.manual_mask = False

    def set_config(self, rec_id, sino_id, proj_geom, vol_geom):
        cfg = astra.astra_dict(self.alg)
        cfg['ReconstructionDataId'] = rec_id
        cfg['ProjectionDataId'] = sino_id
        if 'FBP' in self.alg:
            fbp_filter = self.parameters['FBP_filter'] if 'FBP_filter' in \
                self.parameters.keys() else 'none'
            cfg['FilterType'] = fbp_filter
        if 'projector' in self.parameters.keys():
            proj_id = astra.create_projector(
                self.parameters['projector'], proj_geom, vol_geom)
            cfg['ProjectorId'] = proj_id
        cfg = self.set_options(cfg)
        return cfg

    def delete(self, alg_id, sino_id, rec_id, proj_id):
        astra.algorithm.delete(alg_id)
        astra.data2d.delete(sino_id)
        astra.data2d.delete(rec_id)
        if proj_id:
            astra.projector.delete(proj_id)

    def get_padding_algorithms(self):
        """ A list of algorithms that allow the data to be padded. """
        return ['FBP', 'FBP_CUDA']

    def _get_single(self):
        return 'single'

    def _get_multiple(self):
        return 'multiple'
