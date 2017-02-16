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
.. module:: ptypy_compact
   :platform: Unix
   :synopsis: A plugin to perform ptychography using ptypy

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.utils import register_plugin
from savu.plugins.ptychography.base_ptycho import BasePtycho
import numpy as np
from ptypy.core import Ptycho
from ptypy import utils as u
from copy import deepcopy as copy


@register_plugin
class PtypyBatch(BasePtycho):
    """
    This plugin performs ptychography using the ptypy package. The same parameter set is used across 
    all slices and is based on the output from a previous reconstruction. 
    :param ptyr_file: The ptyd for a previously successful reconstruction. Default: '/dls/i13-1/data/2016/mt14190-1/processing/tomo_processed/ptycho/dls/i13-1/data/2016/mt14190-1/processing/recons/91372/91372_DM_03002.ptyr'.
    """

    def __init__(self):
        super(PtypyBatch, self).__init__("PtypyBatch")

    def pre_process(self):
        b = Ptycho.load_run(self.parameters['ptyr_file'],False) # load in the run but without the data
        p = b.p
        existing_scan = copy(p.scans[p.scans.keys()[0]])
        p.scans.savu = existing_scan
        p.scans.savu.data.source = 'savu'
        p.scans.savu.data.recipe = u.Param()
        p.scan.illumination = b.probe.storages['S00G00'].data
        self.p = p

    def filter_frames(self, data):
        idx = self.get_global_frame_index()# the current frame
        print idx 
        p = self.p
        p.scans.savu.data.recipe.data = data[0]
        positions = self.get_positions()[idx]
        p.scans.savu.data.recipe.positions = positions
        self.p.scans.savu.data.recipe = self.r
        P = Ptycho(self.p,level=5)
        object_stack = P.obj.storages['S00G00'].data.astype(np.float)
        probe_stack = P.probe.storages['S00G00'].data.astype(np.float)
        return [probe_stack, object_stack, positions]#] add fourier error, realspace error

    def get_num_probe_modes(self):
        return self.p.scan.coherence.num_probe_modes

    def set_size_object(self, in_d1, positions, pobj):
        positions = self.get_positions()
        p, r = self.parse_params()
        sh = p.scans.savu.data.shape
        r.data = np.ones((positions.shape[-1],sh,sh))
        p.scans.savu.data.recipe = r
        P = Ptycho(p,level=2)
        object_shape = P.obj.storages['S00G00'].data[0].shape
        self.obj_shape = object_shape + (self.get_num_object_modes(),)
        print "object shape is" + str(self.obj_shape)
    
    def set_size_probe(self, probe_shape):
        self.p, self.r = self.parse_params()
        sh = self.p.scans.savu.data.shape
        self.probe_size = (1,)+tuple(u.expect2(sh)) + (self.get_num_probe_modes(),)
        print "probe size is" + str(self.probe_size)

