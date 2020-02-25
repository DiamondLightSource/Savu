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
.. module:: mask_conditional_evolve3D
   :platform: Unix
   :synopsis: Fast segmentation by evolving the given mask in 3D space using additional\
    mask to constrain the evolution process

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.multi_threaded_plugin import MultiThreadedPlugin
from savu.plugins.utils import register_plugin

from larix.methods.segmentation import MASK_CONDITIONAL_EVOLVE

import numpy as np

@register_plugin
class MaskConditionalEvolve3d(Plugin, MultiThreadedPlugin):
    """
    Fast segmentation by evolving the given 3D mask, the initial mask must be given \
    precisely through the object, otherwise segmentation will be incorrect. Provided additional\
    mask will constrain the evolution process.

    :param threshold: important parameter to control mask propagation. Default: 1.0.
    :param method: method to collect statistics from the mask (mean. median, value). Default: 'mean'.
    :param iterations: The number of iterations. Default: 500.
    :param connectivity: The connectivity of the local neighbourhood. Default: 6.
    :param out_datasets: The default names . Default: ['MASK_EVOLVED'].
    """

    def __init__(self):
        super(MaskConditionalEvolve3d, self).__init__("MaskConditionalEvolve3d")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_3D', 'single')
        in_pData[1].plugin_data_setup('VOLUME_3D', 'single') # the initialisation (mask)
        in_pData[2].plugin_data_setup('VOLUME_3D', 'single') # the conditional mask

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup('VOLUME_3D', 'single')

    def pre_process(self):
        # extract given parameters
        self.threshold = self.parameters['threshold']
        self.iterations = self.parameters['iterations']
        self.connectivity = self.parameters['connectivity']
        self.method = self.parameters['method']

    def process_frames(self, data):
        input_temp = data[0]
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0
        pars = {'input_data' : input_temp,         # input grayscale image
                'maskData' : np.uint8(data[1]),    # generated initialisation mask
                'maskCond' : np.uint8(data[2]),    # conditional mask
                'threhsold' : self.threshold,      # threhsold controls where evolution stops (>=1)
                'iterationsNumb' : self.iterations,# the number of iterations (depends on the size of the phase)
                'connectivity' : self.connectivity,# voxel connectivity rule, choose between 4 (2D), 6, 8 (2D), and 26
                'method' : self.method}            # method to collect statistics from the mask (mean. median, value)  
        if (np.sum(data[1]) > 0):
            mask_evolve = MASK_CONDITIONAL_EVOLVE(pars['input_data'], pars['maskData'],\
                           pars['maskCond'], pars['threhsold'], pars['iterationsNumb'],\
                           pars['connectivity'], pars['method'])
        else:
            mask_evolve = np.uint8(np.zeros(np.shape(data[0])))
        return mask_evolve

    def nInput_datasets(self):
        return 3
    def nOutput_datasets(self):
        return 1
