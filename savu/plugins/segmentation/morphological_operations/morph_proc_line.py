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
.. module:: morph_proc_line
   :platform: Unix
   :synopsis: a Larix module to remove inconsistent gaps in the resulted binary mask by merging the boundaries

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from larix.methods.segmentation import MORPH_PROC_LINE

@register_plugin
class MorphProcLine(Plugin, CpuPlugin):

    def __init__(self):
        super(MorphProcLine, self).__init__("MorphProcLine")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def pre_process(self):
        # extract given parameters
        self.primeclass = self.parameters['primeclass']
        self.CorrectionWindow = self.parameters['correction_window']
        self.iterationsNumb = self.parameters['iterations']

    def process_frames(self, data):
        inputdata = data[0].copy(order='C')
        if (np.sum(inputdata) > 0):
            pars = {'maskdata' : np.uint8(inputdata),\
            'primeClass': self.primeclass,\
            'CorrectionWindow' : self.CorrectionWindow ,\
            'iterationsNumb' : self.iterationsNumb}
            # run class merging module here:
            mask_merged = MORPH_PROC_LINE(pars['maskdata'], pars['primeClass'],
                              pars['CorrectionWindow'], pars['iterationsNumb'])
        else:
            mask_merged = np.uint8(np.zeros(np.shape(inputdata)))
        return mask_merged

    def nInput_datasets(self):
        return 1
    def nOutput_datasets(self):
        return 1
