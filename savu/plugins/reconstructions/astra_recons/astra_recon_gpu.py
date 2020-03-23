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
.. module:: astra_recon_gpu
   :platform: Unix
   :synopsis: Wrapper around the Astra toolbox for gpu reconstruction
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import astra
import numpy as np

from savu.plugins.reconstructions.astra_recons.base_astra_recon \
    import BaseAstraRecon
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.data.plugin_list import CitationInformation
from savu.plugins.utils import register_plugin


@register_plugin
class AstraReconGpu(BaseAstraRecon, GpuPlugin):
    """
    A Plugin to run the astra reconstruction

    :u*param res_norm: Output the residual norm at each iteration\
        (Error in the solution - iterative solvers only). Default: False.
    :u*param algorithm: Reconstruction type (FBP_CUDA|SIRT_CUDA|\
        SART_CUDA (not currently working)|CGLS_CUDA|FP_CUDA|BP_CUDA|\
        SIRT3D_CUDA|CGLS3D_CUDA). Default: 'FBP_CUDA'.
    :u*param FBP_filter: The FBP reconstruction filter type (none|ram-lak|\
        shepp-logan|cosine|hamming|hann|tukey|lanczos|triangular|gaussian|\
        barlett-hann|blackman|nuttall|blackman-harris|blackman-nuttall|\
        flat-top|kaiser|parzen). Default: 'ram-lak'.
    """

    def __init__(self):
        super(AstraReconGpu, self).__init__("AstraReconGpu")
        self.GPU_index = None
        self.res = False
        self.start = 0

    def set_options(self, cfg):
        if 'option' not in list(cfg.keys()):
            cfg['option'] = {}
        cfg['option']['GPUindex'] = self.parameters['GPU_index']
        return cfg

    def nOutput_datasets(self):
        alg = self.parameters['algorithm']
        if self.parameters['res_norm'] is True and 'FBP' not in alg:
            self.res = True
            self.parameters['out_datasets'].append('res_norm')
            return 2
        return 1

    def astra_setup(self):
        options_list = ["FBP_CUDA", "SIRT_CUDA", "SART_CUDA", "CGLS_CUDA",
                        "FP_CUDA", "BP_CUDA", "SIRT3D_CUDA", "CGLS3D_CUDA"]
        if not options_list.count(self.parameters['algorithm']):
            raise Exception("Unknown Astra GPU algorithm.")

    def setup_3D(self):
        pData = self.get_plugin_in_datasets()[0]
        self.sino_dim_detX = \
            pData.get_data_dimension_by_axis_label('x', contains=True)
        self.det_rot = \
            pData.get_data_dimension_by_axis_label('angle', contains=True)
        self.sino_shape = pData.get_shape()
        self.nDims = len(self.sino_shape)
#        self.nCols = self.sino_shape[self.sino_dim_detX]
        self.slice_dir = pData.get_slice_dimension()
        self.slice_func = self.slice_sino(self.nDims)
        l = self.sino_shape[self.sino_dim_detX]
        c = np.linspace(-l / 2.0, l / 2.0, l)
        x, y = np.meshgrid(c, c)
        self.mask_id = False
        mask = np.array((x**2 + y**2 < (l / 2.0)**2), dtype=np.float)
        self.mask = np.transpose(
            np.tile(mask, (self.get_max_frames(), 1, 1)), (1, 0, 2))
        self.manual_mask = True if not self.parameters['sino_pad'] else False

    def astra_3D_recon(self, sino, cors, angles, vol_shape, init):
#        while len(cors) is not self.sino_shape[self.slice_dir]:
#            cors.append(0)
        proj_id = False
        sslice = [slice(None)]*self.nDims
        recon = np.zeros(self.vol_shape)
        recon = np.expand_dims(recon, axis=self.slice_dir)
        if self.res:
            res = np.zeros((self.vol_shape[self.slice_dir], self.iters))

        # create volume geometry
        vol_geom = \
            astra.create_vol_geom(vol_shape[0], vol_shape[2], vol_shape[1])
        # pad the sinogram
        # Don't pad the sinogram if 3d
        # Originally in pad_sino:
        # centre_pad = (0, 0) if '3D' in self.alg else \
        # self.array_pad(cor, sino.shape[self.dim_detX])

        pad_sino = self.pad_sino(self.slice_func(sino, sslice), cors)
        nDets = pad_sino.shape[self.slice_dir]
        trans = (self.slice_dir, self.det_rot, self.sino_dim_detX)
        pad_sino = np.transpose(pad_sino, trans)

        # create projection geom
        vectors = self.create_3d_vector_geom(angles, cors,
                                             sino.shape[self.sino_dim_detX])
        proj_geom = astra.create_proj_geom('parallel3d_vec', nDets,
                                           pad_sino.shape[self.sino_dim_detX],
                                           vectors)
        # create sinogram id
        sino_id = astra.data3d.create("-sino", proj_geom, pad_sino)

        # create reconstruction id
        if init is not None:
            #init = np.transpose(init, (0, 2, 1))  # make this general
            rec_id = astra.data3d.create('-vol', vol_geom, init)
        else:
            rec_id = astra.data3d.create('-vol', vol_geom)

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
        if self.manual_mask:
            recon = self.mask*astra.data3d.get(rec_id)
        else:
            recon = astra.data3d.get(rec_id)

        #recon = astra.data3d.get(rec_id)
        recon = np.transpose(astra.data3d.get(rec_id), (2, 0, 1))
        # delete geometry
        self.delete(alg_id, sino_id, rec_id, proj_id)

        self.start += 1
        if self.res:
            return [recon, res]
        else:
            return recon

    def create_3d_vector_geom(self, angles, cors, detX):
        # add tilt for detector
        # make sure output volume is the correct way
        # add res_norm
        # add a mask
        angles = np.deg2rad(angles)
        vectors = np.zeros((len(angles), 12))
        shift = detX / 2.0 - cors[0]
        for i in range(len(angles)):
            # ray direction
            vectors[i, 0] = np.cos(angles[i])
            vectors[i, 1] = -np.sin(angles[i])
            vectors[i, 2] = 0

            # center of detector
            vectors[i, 3] = -shift*np.sin(angles[i])
            vectors[i, 4] = -shift*np.cos(angles[i])
            vectors[i, 5] = 0

            # vector from detector pixel (0,0) to (0,1)
            vectors[i, 6] = -np.sin(angles[i])
            vectors[i, 7] = -np.cos(angles[i])
            vectors[i, 8] = 0

            # vector from detector pixel (0,0) to (1,0)
            vectors[i, 9] = 0
            vectors[i, 10] = 0
            vectors[i, 11] = 1
        return vectors

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.name = 'citation3'
        cite_info.description = \
            ("The tomography reconstruction algorithm used in this processing \
             pipeline is part of the ASTRA Toolbox")
        cite_info.bibtex = \
            ("@article{palenstijn2011performance,\n" +
             "title={Performance improvements for iterative electron \
             tomography reconstruction using graphics processing units \
             (GPUs)},\n" +
             "author={Palenstijn, WJ and Batenburg, KJ and Sijbers, J},\n" +
             "journal={Journal of structural biology},\n" +
             "volume={176},\n" +
             "number={2},\n" +
             "pages={250--253},\n" +
             "year={2011},\n" +
             "publisher={Elsevier}\n" +
             "}")
        cite_info.endnote = \
            ("%0 Journal Article\n" +
             "%T Performance improvements for iterative electron tomography \
             reconstruction using graphics processing units (GPUs)\n" +
             "%A Palenstijn, WJ\n" +
             "%A Batenburg, KJ\n" +
             "%A Sijbers, J\n" +
             "%J Journal of structural biology\n" +
             "%V 176\n" +
             "%N 2\n" +
             "%P 250-253\n" +
             "%@ 1047-8477\n" +
             "%D 2011\n" +
             "%I Elsevier\n")
        cite_info.doi = "doi: 10.1016/j.jsb.2011.07.017"

        return super(AstraReconGpu, self).get_citation_information() + \
            [cite_info]
