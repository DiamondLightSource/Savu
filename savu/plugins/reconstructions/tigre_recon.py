# Copyright 2018 Diamond Light Source Ltd.
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
.. module:: tigre_recon
   :platform: Unix
   :synopsis: A wrapper around TIGRE software for iterative image reconstruction 

.. moduleauthor:: Reuben Lindroos and Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.gpu_plugin import GpuPlugin

import numpy as np
# IMPORT TIGRE HERE
import tigre
import tigre.algorithms as algs

from savu.plugins.utils import register_plugin
from scipy import ndimage

@register_plugin
class TigreRecon(BaseRecon, GpuPlugin):
    """
    A Plugin to reconstruct full-field tomographic projection data using ierative algorithms from \
    the TIGRE package. 

    :param recon_method: The reconstruction method. Default: 'CGLS'.
    :param iterations: Number of iterations. Default: 20.
    """

    def __init__(self):
        super(TigreRecon, self).__init__("TigreRecon")

    def _shift(self, sinogram, centre_of_rotation):
        centre_of_rotation_shift = (sinogram.shape[0]/2) - centre_of_rotation
        result = ndimage.interpolation.shift(sinogram,
                                             (centre_of_rotation_shift, 0))
        return result
    
    def pre_process(self):
        # extract given parameters and make them 'self'
        self.recon_method = self.parameters['recon_method']
        self.iterations = self.parameters['iterations']
        # DEFINE GEOMETRY AND VOLUME etc. 
       

    def process_frames(self, data):
        centre_of_rotations, angles, self.vol_shape, init  = self.get_frame_params()
        sino = data[0].astype(np.float32) # get a 2D sinogram
        anglesTot, self.DetectorsDimH = np.shape(sino) # get dimensions out of it
        self.anglesRAD = np.deg2rad(angles.astype(np.float32)) # convert to radians
        
        # Reconstruct 2D data (sinogram) with TIGRE
        geo = tigre.geometry(mode = 'parallel', nVoxel = np.array([1, self.vol_shape[0],self.vol_shape[1] ]) ,default=True)
        geo.nDetector = np.array([1,self.DetectorsDimH])
        geo.sDetector = geo.nDetector
        __sino_py = np.float32(np.expand_dims(sino, axis = 1))
        recon = algs.cgls(__sino_py,geo,self.anglesRAD,self.iterations)
        
        return np.swapaxes(recon,0,1)
    
    def get_max_frames(self):
        return 'single'
    
"""
    def get_citation_information(self):
        cite_info1 = CitationInformation()
        cite_info1.name = 'citation1'
        cite_info1.description = \
            ("First-order optimisation algorithm for linear inverse problems.")
        cite_info1.bibtex = \
            ("@article{beck2009,\n" +
             "title={A fast iterative shrinkage-thresholding algorithm for linear inverse problems},\n" +
             "author={Amir and Beck, Mark and Teboulle},\n" +
             "journal={SIAM Journal on Imaging Sciences},\n" +
             "volume={2},\n" +
             "number={1},\n" +
             "pages={183--202},\n" +
             "year={2009},\n" +
             "publisher={SIAM}\n" +
             "}")
        cite_info1.endnote = \
            ("%0 Journal Article\n" +
             "%T A fast iterative shrinkage-thresholding algorithm for linear inverse problems\n" +
             "%A Beck, Amir\n" +
             "%A Teboulle, Mark\n" +
             "%J SIAM Journal on Imaging Sciences\n" +
             "%V 2\n" +
             "%N 1\n" +
             "%P 183--202\n" +
             "%@ --\n" +
             "%D 2009\n" +
             "%I SIAM\n")
        cite_info1.doi = "doi: "
        return cite_info1
"""