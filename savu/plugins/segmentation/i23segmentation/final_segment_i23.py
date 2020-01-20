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
.. module:: creates final segmentation for i23 data, apply at the end of the process list
   :platform: Unix
   :synopsis: creates final segmentation for i23 data, apply at the end of the process list

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np

@register_plugin
class FinalSegmentI23(Plugin, CpuPlugin):
    """
    Apply at the end when all objects have been segmented independently (crystal, liquor, whole object)

    :param set_classes_val: Set the values for all 4 classes (crystal, liquor, loop, vacuum). Default: [255, 128, 64, 0].
    """

    def __init__(self):
        super(FinalSegmentI23, self).__init__("FinalSegmentI23")

    def setup(self):

        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def pre_process(self):
        # extract given parameters
        self.set_classes_val = self.parameters['set_classes_val']

    def process_frames(self, data):
        CrystSegm = data[0] 
        LiquorSegm = data[1]
        WholeObjSegm = data[2]
        LoopSegm = WholeObjSegm - LiquorSegm
        notnull_ind = np.where(LoopSegm == 1) 
        LoopSegm[notnull_ind] = self.set_classes_val[2]
        
        FinalSegm = CrystSegm+LiquorSegm+LoopSegm
        # now FinalSegm has got 4 values [0,1,2,loop_val] for [vacuum, liquor, crystal, loop]
        
        ind_d = np.where(FinalSegm == 0) # vacuum
        FinalSegm[ind_d] = self.set_classes_val[3]
        ind_d = np.where(FinalSegm == 1) # liquor
        FinalSegm[ind_d] = self.set_classes_val[1]
        ind_d = np.where(FinalSegm == 2) # crystal
        FinalSegm[ind_d] = self.set_classes_val[0]
        return [FinalSegm]

    def nInput_datasets(self):
        return 3
    def nOutput_datasets(self):
        return 1
