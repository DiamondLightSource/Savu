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
.. module:: ptypy_batch
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
import h5py as h5


#@register_plugin
class PtypyBatch(BasePtycho):
    def __init__(self):
        super(PtypyBatch, self).__init__("PtypyBatch")

    def pre_process(self):
        b = Ptycho.load_run(self.parameters['ptyr_file'], False) # load in the run but without the data
        p = b.p
        existing_scan = copy(p.scans[list(p.scans.keys())[0]])
        del p.scans[list(p.scans.keys())[0]]
        p.scans.savu = existing_scan
        p.scans.savu.data.source = 'savu'
        p.scans.savu.data.recipe = u.Param()
        if self.parameters['mask_file'] is not None:
            p.scans.savu.data.recipe.mask = h5.File(self.parameters['mask_file'],'r')[self.parameters['mask_entry']][...]
        else:
            p.scans.savu.data.recipe.mask = np.ones(self.in_shape[-2:])
        p.scan.illumination = b.probe.storages['S00G00'].data
        self.p = p

    def filter_frames(self, data):
#         idx = self.get_global_frame_index()# the current frame
        p = self.p
        p.scans.savu.data.recipe.data = data[0]
        positions = self.get_positions()[0]# just assume zero for now
        p.scans.savu.data.recipe.positions = positions.T[:600]
        P = Ptycho(p,level=5)
        object_stack = P.obj.storages['S00G00'].data.astype(np.float)
        probe_stack = P.probe.storages['S00G00'].data.astype(np.float)
        return [probe_stack, object_stack, positions]#] add fourier error, realspace error

    def setup(self):
        in_datasets, out_datasets = self.get_datasets()
        self.in_shape = in_datasets[0].get_shape()
        in_pData, __out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())
        self.in_slice_dirs= np.array(in_pData[0].get_slice_directions())
        self.in_core_dirs= np.sort(np.array(in_pData[0].get_core_directions()))# sort them to get in the right order
        self.b = Ptycho.load_run(self.parameters['ptyr_file'],False)
        self.p = self.b.p
        BasePtycho.setup(self)

    def get_num_probe_modes(self):
        return self.p.scan.coherence.num_probe_modes

    def get_num_object_modes(self):
        return self.p.scan.coherence.num_object_modes

    def set_size_object(self, in_d1, positions, pobj):
        first_core = self.in_core_dirs[0]
        last_core = self.in_core_dirs[-1]
        start_shape = self.in_shape[:first_core]
        self.obj_shape=self.b.obj.storages['S00G00'].data.shape
        #print "object shape is" + str(self.obj_shape)

    def set_size_probe(self, probe_shape):
        first_core = self.in_core_dirs[0]
        last_core = self.in_core_dirs[-1]
        start_shape = self.in_shape[:first_core]
        self.probe_size=start_shape+self.b.probe.storages['S00G00'].data.shape
        #print "probe size is" + str(self.probe_size)
