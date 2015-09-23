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
from savu.plugins.base_recon import BaseRecon
#from savu.data.plugin_info import CitationInfomration

"""
.. module:: cgls_recon
   :platform: Unix
   :synopsis: Wrapper around the CCPi cgls reconstruction
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.driver.cpu_plugin import CpuPlugin

import numpy as np
import ccpi_reconstruction
from savu.plugins.utils import register_plugin


@register_plugin
class CglsRecon(BaseRecon, CpuPlugin):
    """
     A Plugin to run the CCPi cgls reconstruction
    
    :param number_of_iterations: Number of Iterations if an iterative method is used . Default: 5.
    :param resolution: Determines the number of output voxels where resolution = n_pixels/n_voxels. Default: 1.
    :param number_of_threads: Number of OMP threads. Default: 1
    """
    
    def __init__(self):
        super(CglsRecon, self).__init__("CglsRecon") 
        
    def pre_process(self, exp):
        in_data = self.get_data_objects(exp.index, "in_data")
        angles = in_data[0].meta_data.get_meta_data("rotation_angle")
        params = [angles]
        return params

    def reconstruct(self, sinogram, centre_of_rotations, vol_shape, params):
        angles = params[0]
        nthreads = self.parameters['number_of_threads']
        num_iterations = self.parameters['number_of_iterations']
        resolution = self.parameters['resolution']

        pixels = np.hstack([np.reshape(sinogram.astype(np.float32), \
                            (sinogram.shape[0], 1, sinogram.shape[1]))]*4)

        voxels = ccpi_reconstruction.cgls(pixels, angles.astype(np.float32), \
                                            centre_of_rotations, resolution, \
                                            num_iterations, nthreads)

        #voxels = voxels[:160,:160,1]   
         
        return voxels
        
