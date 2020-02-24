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
.. module:: module to remove gaps in the provided binary mask by merging the boundaries
   :platform: Unix
   :synopsis: module to remove gaps in the provided binary mask by merging the boundaries

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from i23.methods.segmentation import MASK_CORR_BINARY

@register_plugin
class MergeBinaryMask(Plugin, CpuPlugin):
    """
    A plugin to remove gaps in the provided binary mask by merging the boundaries

    :param selectedclass: The selected class for merging. Default: 0.
    :param correction_window: The size of the correction window. Default: 9.
    :param iterations: The number of iterations for segmentation. Default: 10.
    :param pattern: pattern to apply this to. Default: "VOLUME_XY".
    """

    def __init__(self):
        super(MergeBinaryMask, self).__init__("MergeBinaryMask")

    def setup(self):    
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
    
    def pre_process(self):
        # extract given parameters
        self.selectedClass = self.parameters['selectedclass']
        self.CorrectionWindow = self.parameters['correction_window']        
        self.iterationsNumb = self.parameters['iterations']        

    def process_frames(self, data):
        # run class merging here:
        inputdata = data[0].copy(order='C')
        pars = {'maskdata' : np.uint8(inputdata),\
        'selectedClass': self.selectedClass,\
        'CorrectionWindow' : self.CorrectionWindow ,\
        'iterationsNumb' : self.iterationsNumb}               
        
        mask_merged = MASK_CORR_BINARY(pars['maskdata'], pars['selectedClass'],\
                                       pars['CorrectionWindow'], pars['iterationsNumb'])       
        return mask_merged
    
    def nInput_datasets(self):
        return 1
    def nOutput_datasets(self):
        return 1
    
