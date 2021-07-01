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
.. module:: ccpi_cgls_recon
   :platform: Unix
   :synopsis: Wrapper around the CCPi cgls reconstruction algorithm.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import numpy as np

from ccpi.reconstruction.parallelbeam import alg as ccpi_alg

from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.reconstructions.base_recon import BaseRecon


@register_plugin
class CcpiCglsRecon(BaseRecon, CpuPlugin):
    """
    """

    def __init__(self):
        super(CcpiCglsRecon, self).__init__("CcpiCglsRecon")

    def pre_process(self):
        self.n_iters = self.parameters['n_iterations']
        self.res = self.parameters['resolution']
        in_data = self.get_in_datasets()[0]
        in_pData = self.get_plugin_in_datasets()[0]
        det_x = in_pData.get_data_dimension_by_axis_label('detector_x')
        self.width = in_data.get_shape()[det_x]

    def process_frames(self, data):
        sino = data[0]
        cors, angles, vol_shape, init = self.get_frame_params()

        voxels = ccpi_alg.cgls(sino.astype(np.float32),
                               angles.astype(np.float32), cors[0],
                               self.res, self.n_iters, 1,
                               self.parameters['log'])

        # need to get left and right shift and crop
        pad_start, pad_end = self.array_pad(cors[0], self.width)
        return np.transpose(voxels[pad_start:pad_end, pad_start:pad_end, :], (0, 2, 1))

    def array_pad(self, ctr, nPixels):
        width = nPixels - 1.0
        alen = ctr
        blen = width - ctr
        mid = (width-1.0)/2.0
        shift = round(abs(blen-alen))
        p_low = 0 if (ctr > mid) else shift
        p_high = shift + 0 if (ctr > mid) else 0
        pad = max(p_low, p_high)
        if pad == 0:
            return 0, -1
        return int(pad/2-1), int(-np.ceil(pad/2.0))

    def get_max_frames(self):
        # this algorithm requires a multiple of 8 frames
        default = 16
        n_frames = self.parameters['n_frames']
        if n_frames % 8 != 0:
            n_frames = default
            logging.warn('incorrect number of frames requested for cgls_recon,'
                         ' using %s', default)
        return n_frames
