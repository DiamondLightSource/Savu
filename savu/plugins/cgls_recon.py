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
.. module:: cgls_recon
   :platform: Unix
   :synopsis: Wrapper around the CCPi cgls reconstruction
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

from savu.plugins.cpu_plugin import CpuPlugin

"""

from savu.plugins.cpu_plugin import CpuPlugin

import numpy as np

import ccpi

class CglsRecon(BaseRecon, CpuPlugin):
    """
     A Plugin to run the CCPi cgls reconstruction
    
    :param number_of_iterations: Number of Iterations if an iterative method is used . Default: 5.
    :param resolution: Determines the number of output voxels where resolution = n_pixels/n_voxels. Default: 1.
    :param number_of_threads: Number of OMP threads. Default: 1
    """
    
    def __init__(self):
        super(CglsRecon, self).__init__("CglsRecon") 
        

    def reconstruct(self, sinogram, centre_of_rotation, angles, shape, center):
        
        nthreads = self.parameters['number_of_threads']
        num_iterations = self.parameters['number_of_iterations']
        resolution = self.parameters['resolution']

        pixels = np.hstack([np.reshape(sinogram.astype(np.float32), (sinogram.shape[0], 1, sinogram.shape[1]))]*4)
        
        
        voxels = ccpi.cgls(np.log(pixels), angles.astype(np.float32), centre_of_rotation, \
                           resolution, num_iterations, nthreads)
                           
#        voxels = np.lib.pad(voxels[:160,:160,2], (37,37), 'constant', constant_values=0)
        voxels = voxels[:160,:160,2]
        
        return voxels
        