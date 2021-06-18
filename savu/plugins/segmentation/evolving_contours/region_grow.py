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
.. module:: region_grow
   :platform: Unix
   :synopsis: Fast region-grow type segmentation (2D) from Larix toolbox to evolve a given mask

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

from larix.methods.segmentation import REGION_GROW
import numpy as np

@register_plugin
class RegionGrow(Plugin, CpuPlugin):

    def __init__(self):
        super(RegionGrow, self).__init__("RegionGrow")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        in_pData[1].plugin_data_setup(self.parameters['pattern'], 'single') # the initialisation (mask)

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def pre_process(self):
        # extract given parameters
        self.threshold = self.parameters['threshold']
        self.iterations = self.parameters['iterations']
        self.connectivity = self.parameters['connectivity']
        if (str(self.parameters['method']) == 'mean'):
            self.method = 'mean'
        elif (str(self.parameters['method']) == 'median'):
            self.method = 'median'
        else:
            self.method = 'value'

    def process_frames(self, data):
        input_temp = data[0]
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0

        pars = {'input_data' : input_temp, # input grayscale image
        'maskData' : np.uint8(data[1]),    # generated initialisation mask
        'threhsold' : self.threshold,      # threhsold controls where evolution stops (>=1)
        'iterationsNumb' : self.iterations,# the number of iterations (depends on the size of the phase)
        'connectivity' : self.connectivity,# voxel connectivity rule, choose between 4 (2D), 6, 8 (2D), and 26
        'method' : self.method}            # method to collect statistics from the mask (mean. median, value)

        # run the method
        if (np.sum(data[1]) > 0):
            mask_evolve = REGION_GROW(pars['input_data'], pars['maskData'],\
                           pars['threhsold'], pars['iterationsNumb'],\
                           pars['connectivity'], pars['method'])
        else:
            mask_evolve = np.uint8(np.zeros(np.shape(data[0])))
        return mask_evolve

    def nInput_datasets(self):
        return 2
    def nOutput_datasets(self):
        return 1
    def get_max_frames(self):
        return 'single'
