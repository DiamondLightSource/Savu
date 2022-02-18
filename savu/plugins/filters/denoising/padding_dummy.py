# Copyright 2019 Diamond Light Source Ltd.
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
.. module:: padding_dummy
   :platform: Unix
   :synopsis: a plugin to test 3D padding

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

#from savu.plugins.plugin import Plugin
from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
import numpy as np


@register_plugin
class PaddingDummy(BaseRecon, CpuPlugin):

    def __init__(self):
        super(PaddingDummy, self).__init__("PaddingDummy")
        self.Horiz_det = None
        self.pad = None

    def set_filter_padding(self, in_pData, out_pData):
        self.pad = self.parameters['padding']
        in_data = self.get_in_datasets()[0]
        det_y = in_data.get_data_dimension_by_axis_label('detector_y')
        pad_det_y = '%s.%s' % (det_y, self.pad)
        pad_dict = {'pad_directions': [pad_det_y], 'pad_mode': 'edge'}
        in_pData[0].padding = pad_dict
        out_pData[0].padding = pad_dict

    def setup(self):
        #in_dataset = self.get_in_datasets()[0]
        #procs = self.exp.meta_data.get("processes")
        #procs = len([i for i in procs if 'GPU' in i])
        #dim = in_dataset.get_data_dimension_by_axis_label('detector_y')
        in_dataset = self.get_in_datasets()[0]
        procs = self.exp.meta_data.get("processes")
        procs = len([i for i in procs if 'GPU' in i])

        self.nSlices = 5
        self._set_max_frames(self.nSlices)
        super(PaddingDummy, self).setup()

    def process_frames(self, data):
        cor, angles, self.vol_shape, init = self.get_frame_params()
        projdata3D = data[0].astype(np.float32)
        dim_tuple = np.shape(projdata3D)
        self.Horiz_det = dim_tuple[self.det_dimX_ind]
        res = np.zeros((self.Horiz_det, dim_tuple[1], self.Horiz_det))
        return res

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        out_pData = self.get_plugin_out_datasets()[0]
        detY = in_pData.get_data_dimension_by_axis_label('detector_y')
        # ! padding the vertical detector !
        self.Vert_det = in_pData.get_shape()[detY] + 2 * self.pad

        in_pData = self.get_plugin_in_datasets()
        self.det_dimX_ind = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        self.det_dimY_ind = in_pData[0].get_data_dimension_by_axis_label('detector_y')

    def _set_max_frames(self, frames):
        self._max_frames = frames

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
