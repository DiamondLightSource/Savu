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
from savu.plugins.base_recon import BaseRecon
from savu.data.process_data import CitationInfomration

"""
.. module:: astra_recon
   :platform: Unix
   :synopsis: Wrapper around the Astra toolbox for reconstruction
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.cpu_plugin import CpuPlugin

import numpy as np

import astra


class AstraRecon(BaseRecon, CpuPlugin):
    """
    A Plugin to run the astra reconstruction
    """

    def __init__(self):
        super(AstraRecon, self).__init__("AstraRecon")

    def populate_default_parameters(self):
        super(AstraRecon, self).populate_default_parameters()
        self.parameters['number_of_itterations'] = 20
        self.parameters['reconstruction_type'] = 'SIRT'

    def reconstruct(self, sinogram, centre_of_rotation, angles, shape, center):

        ctr = centre_of_rotation
        width = sinogram.shape[1]
        pad = 50

        sino = np.nan_to_num(sinogram)

        # pad the array so that the centre of rotation is in the middle
        alen = ctr
        blen = width - ctr
        mid = width / 2.0

        if (ctr > mid):
            plow = pad
            phigh = (alen - blen) + pad
        else:
            plow = (blen - alen) + pad
            phigh = pad

        logdata = np.log(sino+1)
        sinogram = np.pad(logdata, ((0, 0), (int(plow), int(phigh))),
                          mode='reflect')

        width = sinogram.shape[1]

        vol_geom = astra.create_vol_geom(shape[0], shape[1])
        proj_geom = astra.create_proj_geom('parallel', 1.0, width,
                                           np.deg2rad(angles))

        sinogram_id = astra.data2d.create("-sino", proj_geom, sinogram)

        # Create a data object for the reconstruction
        rec_id = astra.data2d.create('-vol', vol_geom)

        proj_id = astra.create_projector('strip', proj_geom, vol_geom)

        cfg = astra.astra_dict(self.parameters['reconstruction_type'])
        cfg['ReconstructionDataId'] = rec_id
        cfg['ProjectionDataId'] = sinogram_id
        cfg['ProjectorId'] = proj_id

        # Create the algorithm object from the configuration structure
        alg_id = astra.algorithm.create(cfg)
        # Run 20 iterations of the algorithm
        itterations = int(self.parameters['number_of_itterations'])
        # This will have a runtime in the order of 10 seconds.
        astra.algorithm.run(alg_id, itterations)
        # Get the result
        rec = astra.data2d.get(rec_id)

        # Clean up.
        astra.algorithm.delete(alg_id)
        astra.data2d.delete(rec_id)
        astra.data2d.delete(sinogram_id)

        return rec

    def get_citation_inforamtion(self):
        cite_info = CitationInfomration()
        cite_info.description = \
            ("The reconstruction used to create this output is described in " +
             "this publication")
        cite_info.bibtex = \
            ("@article{palenstijn2011performance,\n" +
             "title={Performance improvements for iterative electron " +
             "tomography reconstruction using graphics processing units " +
             "(GPUs)},\n" +
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
             "%T Performance improvements for iterative electron tomography " +
             "reconstruction using graphics processing units (GPUs)\n" +
             "%A Palenstijn, WJ\n" +
             "%A Batenburg, KJ\n" +
             "%A Sijbers, J\n" +
             "%J Journal of structural biology\n" +
             "%V 176\n" +
             "%N 2\n" +
             "%P 250-253\n" +
             "%@ 1047-8477\n" +
             "%D 2011\n" +
             "%I Elsevier")
        cite_info.doi = "http://dx.doi.org/10.1016/j.jsb.2011.07.017"
        return cite_info
