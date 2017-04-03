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
import copy

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation


class BaseAstraRecon(BaseRecon):
    """
    A Plugin to perform Astra toolbox reconstruction

    :u*param FBP_filter: The FBP reconstruction filter type (none|ram-lak|\
        shepp-logan|cosine|hamming|hann|tukey|lanczos|triangular|gaussian|\
        barlett-hann|blackman|nuttall|blackman-harris|blackman-nuttall|\
        flat-top|kaiser|parzen). Default: 'ram-lak'.
    :u*param n_iterations: Number of Iterations if an iterative method\
        is used . Default: 1.
    """

    def __init__(self, name='BaseAstraRecon'):
        super(BaseAstraRecon, self).__init__(name)
        self.res = False

    def setup(self):
        super(BaseAstraRecon, self).setup()
        out_dataset = self.get_out_datasets()
        # if res_norm is required then setup another output dataset
        if len(out_dataset) is 2:
            self.res = True
            out_pData = self.get_plugin_out_datasets()
            in_data = self.get_in_datasets()[0]
            dim_detX = in_data.find_axis_label_dimension('y', contains=True)
            shape = (in_data.get_shape()[dim_detX],
                     self.parameters['number_of_iterations'])
            label = ['vol_y.voxel', 'iteration.number']
            pattern = {'name': 'SINOGRAM', 'slice_dir': (0,), 'core_dir': (1,)}
            out_dataset[1].create_dataset(axis_labels=label, shape=shape)
            out_dataset[1].add_pattern(pattern['name'],
                                       slice_dir=pattern['slice_dir'],
                                       core_dir=pattern['core_dir'])
            out_pData[1].plugin_data_setup(pattern['name'],
                                           self._get_frame_type())

    def pre_process(self):
        self.alg = self.parameters['reconstruction_type']
        self.iters = self.parameters['n_iterations']
        if '3D' in self.alg:
            self.setup_3D()
            self.process_frames = self.astra_3D_recon
        else:
            self.setup_2D()
            self.process_frames = self.astra_2D_recon
        self.vol_shape = self.get_vol_shape()

    def setup_2D(self):
        pData = self.get_plugin_in_datasets()[0]
        dim_detX = pData.get_data_dimension_by_axis_label('x', contains=True)
        dim_rot = pData.get_data_dimension_by_axis_label('rot', contains=True)

        self.sino_shape = pData.get_shape()
        self.nDims = len(self.sino_shape)
        self.slice_dir = pData.get_slice_dimension()

        self.sino_dim_detX = dim_detX-1 if self.nDims is 3 and\
            self.slice_dir < dim_detX else dim_detX
        self.sino_dim_rot = dim_rot-1 if self.nDims is 3 and\
            self.slice_dir < dim_rot else dim_rot

        self.nCols = self.sino_shape[dim_detX]
        self.nSinos = self.sino_shape[self.slice_dir] if self.nDims is 3 else 1
        self.slice_func = self.slice_sino(self.nDims)
        l = self.sino_shape[dim_detX]
        c = np.linspace(-l/2.0, l/2.0, l)
        x, y = np.meshgrid(c, c)
        self.mask = np.array((x**2 + y**2 < (l/2.0)**2), dtype=np.float)
        self.mask_id = True if not self.parameters['sino_pad'] and 'FBP' not \
            in self.alg else False
        if not self.parameters['sino_pad']:
            self.manual_mask = copy.copy(self.mask)
            self.manual_mask[self.manual_mask == 0] = np.nan
        else:
            self.manual_mask = False

    def slice_sino(self, nDims):
        if nDims is 2:
            return lambda x, sslice: np.expand_dims(
                x, axis=self.slice_dir)[sslice]
        else:
            return lambda x, sslice: x[sslice]

    def astra_2D_recon(self, data):
        logging.debug("running astra_2D_recon")
        sino = data[0]
        cors, angles, vol_shape, init = self.get_frame_params()
        sslice = [slice(None)]*self.nDims
        recon = np.zeros(self.vol_shape)
        if self.nDims is 2:
            recon = np.expand_dims(recon, axis=self.slice_dir)
        if self.res:
            res = np.zeros((self.vol_shape[self.slice_dir], self.iters))
        if self.nDims is 2:
            res = np.expand_dims(recon, axis=self.slice_dir)

        proj_id = False
        # create volume geom

        astra_vol_shape = list(vol_shape)
        del astra_vol_shape[self.slice_dir]
        vol_geom = astra.create_vol_geom(astra_vol_shape)

        for i in range(self.nSinos):
            sslice[self.slice_dir] = i
            try:
                cor = cors[i]
            except:
                cor = cors[0]

            pad_sino = self.pad_sino(self.slice_func(sino, sslice), cor)

            # create projection geom
            proj_geom = astra.create_proj_geom(
                'parallel', 1.0, pad_sino.shape[self.sino_dim_detX],
                np.deg2rad(angles))

            pad_sino = \
                np.transpose(pad_sino, (self.sino_dim_rot, self.sino_dim_detX))

            # create sinogram id
            sino_id = astra.data2d.create("-sino", proj_geom, pad_sino)

            # create reconstruction id
            if init is not None:
                rec_id = astra.data2d.create('-vol', vol_geom, init[sslice])
            else:
                rec_id = astra.data2d.create('-vol', vol_geom)

            if self.mask_id:
                self.mask_id = astra.data2d.create('-vol', vol_geom, self.mask)

            # setup configuration options
            cfg = self.set_config(rec_id, sino_id, proj_geom, vol_geom)

            # create algorithm id
            alg_id = astra.algorithm.create(cfg)

            # run algorithm
            if self.res:
                for j in range(self.iters):
                    # Run a single iteration
                    astra.algorithm.run(alg_id, 1)
                    res[i, j] = astra.algorithm.get_res_norm(alg_id)
            else:
                astra.algorithm.run(alg_id, self.iters)

            # get reconstruction matrix
            if self.manual_mask is not False:
                recon[sslice] = self.manual_mask*astra.data2d.get(rec_id)
            else:
                recon[sslice] = astra.data2d.get(rec_id)

            # delete geometry
            self.delete(alg_id, sino_id, rec_id, proj_id)

        if self.res:
            return [recon, res]
        else:
            return recon

    def set_config(self, rec_id, sino_id, proj_geom, vol_geom):
        cfg = astra.astra_dict(self.alg)
        cfg['ReconstructionDataId'] = rec_id
        cfg['ProjectionDataId'] = sino_id
        if 'FBP' in self.alg:
            cfg['FilterType'] = self.parameters['FBP_filter']
        if 'projector' in self.parameters.keys():
            proj_id = astra.create_projector(
                self.parameters['projector'], proj_geom, vol_geom)
            cfg['ProjectorId'] = proj_id
        # mask not currently working correctly for SIRT or SART algorithms
        sirt_or_sart = [a for a in ['SIRT', 'SART'] if a in self.alg]
        if self.mask_id and not sirt_or_sart:
            cfg['option'] = {}
            cfg['option']['ReconstructionMaskId'] = self.mask_id
        cfg = self.set_options(cfg)
        return cfg

    def delete(self, alg_id, sino_id, rec_id, proj_id):
        astra.algorithm.delete(alg_id)
        if self.mask_id:
            astra.data2d.delete(self.mask_id)
        astra.data2d.delete(sino_id)
        astra.data2d.delete(rec_id)
        if proj_id:
            astra.projector.delete(proj_id)

    def pad_sino(self, sino, cor):
        centre_pad = (0, 0) if '3D' in self.alg else \
            self.array_pad(cor, sino.shape[self.sino_dim_detX])
        sino_width = sino.shape[self.sino_dim_detX]
        new_width = sino_width + max(centre_pad)
        sino_pad = \
            int(math.ceil(float(sino_width)/new_width * self.sino_pad)/2)
        pad = np.array([sino_pad]*2) + centre_pad
        pad_tuples = [(0, 0)]*(len(sino.shape)-1)
        pad_tuples.insert(self.sino_dim_detX, tuple(pad))
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

    def get_citation_information(self):
        cite_info1 = CitationInformation()
        cite_info1.name = 'citation1'
        cite_info1.description = \
            ("The tomography reconstruction algorithm used in this processing \
             pipeline is part of the ASTRA Toolbox")
        cite_info1.bibtex = \
            ("@article{van2016fast,\n" +
             "title={Fast and flexible X-ray tomography using the ASTRA \
             toolbox},\n" +
             "author={van Aarle, Wim and Palenstijn, Willem Jan and Cant, \
             Jeroen and Janssens, Eline and Bleichrodt, Folkert and \
             Dabravolski, Andrei and De Beenhouwer, Jan and Batenburg, K Joost\
             and Sijbers, Jan},\n" +
             "journal={Optics Express},\n" +
             "volume={24},\n" +
             "number={22},\n" +
             "pages={25129--25147},\n" +
             "year={2016},\n" +
             "publisher={Optical Society of America}\n" +
             "}")
        cite_info1.endnote = \
            ("%0 Journal Article\n" +
             "%T Fast and flexible X-ray tomography using the ASTRA \
             toolbox\n" +
             "%A van Aarle, Wim\n" +
             "%A Palenstijn, Willem Jan\n" +
             "%A Cant, Jeroen\n" +
             "%A Janssens, Eline\n" +
             "%A Bleichrodt, Folkert\n" +
             "%A Dabravolski, Andrei\n" +
             "%A De Beenhouwer, Jan\n" +
             "%A Batenburg, K Joost\n" +
             "%A Sijbers, Jan\n" +
             "%J Optics Express\n" +
             "%V 24\n" +
             "%N 22\n" +
             "%P 25129-25147\n" +
             "%@ 1094-4087\n" +
             "%D 2016\n" +
             "%I Optical Society of America\n")
        cite_info1.doi = "doi: 10.1364/OE.24.025129"

        cite_info2 = CitationInformation()
        cite_info2.name = 'citation2'
        cite_info2.description = \
            ("The tomography reconstruction algorithm used in this processing \
             pipeline is part of the ASTRA Toolbox")
        cite_info2.bibtex = \
            ("@article{van2015astra,\n" +
             "title={The ASTRA Toolbox: A platform for advanced algorithm \
             development in electron tomography},\n" +
             "author={van Aarle, Wim and Palenstijn, Willem Jan and \
             De Beenhouwer, Jan and Altantzis, Thomas and Bals, Sara and \
             Batenburg, K Joost and Sijbers, Jan},\n" +
             "journal={Ultramicroscopy},\n" +
             "volume={157},\n" +
             "pages={35--47},\n" +
             "year={2015},\n" +
             "publisher={Elsevier}\n" +
             "}")
        cite_info2.endnote = \
            ("%0 Journal Article\n" +
             "%T Numerical removal of ring artifacts in microtomography\n" +
             "%A Raven, Carsten\n" +
             "%J Review of scientific instruments\n" +
             "%V 69\n" +
             "%N 8\n" +
             "%P 2978-2980\n" +
             "%@ 0034-6748\n" +
             "%D 1998\n" +
             "%I AIP Publishing")
        cite_info2.doi = "doi: 10.1364/OE.24.025129"

        return [cite_info1, cite_info2]
