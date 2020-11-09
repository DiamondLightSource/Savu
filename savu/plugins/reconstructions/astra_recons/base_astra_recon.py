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

import astra
import numpy as np

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation


class BaseAstraRecon(BaseRecon):
    """
    A Plugin to perform Astra toolbox reconstruction

    :u*param n_iterations: Number of Iterations - only valid for iterative \
        algorithms. Default: 1.
    """

    def __init__(self, name='BaseAstraRecon'):
        super(BaseAstraRecon, self).__init__(name)
        self.res = False

    def setup(self):
        self.alg = self.parameters['algorithm']
        self.get_max_frames = self._get_multiple if '3D' in self.alg else self._get_single

        super(BaseAstraRecon, self).setup()
        out_dataset = self.get_out_datasets()

        # if res_norm is required then setup another output dataset
        if len(out_dataset) == 2:
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
            self.process_frames = self.astra_3D_recon
        else:
            self.setup_2D()
            self.process_frames = self.astra_2D_recon

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

    def set_mask(self, shape):
        l = self.get_plugin_out_datasets()[0].get_shape()[0]
        c = np.linspace(-l / 2.0, l / 2.0, l)
        x, y = np.meshgrid(c, c)
        r = (shape[self.dim_detX]-1)*self.parameters['ratio']

        outer_pad = True if self.parameters['outer_pad'] and self.padding_alg\
            else False
        if not outer_pad:
            self.manual_mask = \
                np.array((x**2 + y**2 < (r / 2.0)**2), dtype=np.float)
            self.manual_mask[self.manual_mask == 0] = np.nan
        else:
            self.manual_mask = False

    def astra_2D_recon(self, data):
        sino = data[0]
        cor, angles, vol_shape, init = self.get_frame_params()
        angles = np.deg2rad(angles)
        if self.res:
            res = np.zeros(self.len_res)
        # create volume geom
        vol_geom = astra.create_vol_geom(vol_shape)
        # create projection geom
        det_width = sino.shape[self.dim_detX]
        proj_geom = astra.create_proj_geom('parallel', 1.0, det_width, angles)
        sino = np.transpose(sino, (self.dim_rot, self.dim_detX))

        # create sinogram id
        sino_id = astra.data2d.create("-sino", proj_geom, sino)
        # create reconstruction id
        if init is not None:
            rec_id = astra.data2d.create('-vol', vol_geom, init)
        else:
            rec_id = astra.data2d.create('-vol', vol_geom)

#        if self.mask_id:
#            self.mask_id = astra.data2d.create('-vol', vol_geom, self.mask)
        # setup configuration options
        cfg = self.set_config(rec_id, sino_id, proj_geom, vol_geom)
        # create algorithm id
        alg_id = astra.algorithm.create(cfg)
        # run algorithm
        if self.res:
            for j in range(self.iters):
                # Run a single iteration
                astra.algorithm.run(alg_id, 1)
                res[j] = astra.algorithm.get_res_norm(alg_id)
        else:
            astra.algorithm.run(alg_id, self.iters)
        # get reconstruction matrix

        if self.manual_mask is not False:
            recon = self.manual_mask*astra.data2d.get(rec_id)
        else:
            recon = astra.data2d.get(rec_id)

        # delete geometry
        self.delete(alg_id, sino_id, rec_id, False)
        return [recon, res] if self.res else recon

    def set_config(self, rec_id, sino_id, proj_geom, vol_geom):
        cfg = astra.astra_dict(self.alg)
        cfg['ReconstructionDataId'] = rec_id
        cfg['ProjectionDataId'] = sino_id
        if 'FBP' in self.alg:
            fbp_filter = self.parameters['FBP_filter'] if 'FBP_filter' in \
                list(self.parameters.keys()) else 'none'
            cfg['FilterType'] = fbp_filter
        if 'projector' in list(self.parameters.keys()):
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
