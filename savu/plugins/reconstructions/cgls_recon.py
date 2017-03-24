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
.. module:: cgls_recon
   :platform: Unix
   :synopsis: Wrapper around the CCPi cgls reconstruction

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.driver.cpu_plugin import CpuPlugin

import numpy as np
import ccpi
from savu.plugins.utils import register_plugin

from savu.plugins.reconstructions.base_recon import BaseRecon


@register_plugin
class CglsRecon(BaseRecon, CpuPlugin):
    """
     A Plugin to run the CCPi cgls reconstruction

    :param number_of_iterations: Number of iterations. Default: 5.
    :param resolution: number of output voxels \
        (res = n_pixels/n_voxels). Default: 1.
    :param number_of_threads: Number of OMP threads. Default: 1
    """

    def __init__(self):
        super(CglsRecon, self).__init__("CglsRecon")

    def process_frames(self, data):
        sino = data[0]
        cors, angles, vol_shape, init = self.get_frame_params()

        nthreads = self.parameters['number_of_threads']
        num_iterations = self.parameters['number_of_iterations']
        resolution = self.parameters['resolution']

        voxels = ccpi.cgls(sino.astype(np.float32), angles.astype(np.float32),
                           cors[0], resolution, num_iterations, nthreads)

        voxels = voxels[:160, :160, ...]
        if voxels.ndim is 3:
            voxels = np.transpose(voxels, (0, 2, 1))
            if voxels.shape[1] > sino.shape[1]:
                diff = voxels.shape[1] - sino.shape[1]
                voxels = voxels[:, :-diff, :]

        return voxels
