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
.. module:: Fast segmentation by evolving the given mask in 3D
   :platform: Unix
   :synopsis: Fast segmentation by evolving the given mask in 3D

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.multi_threaded_plugin import MultiThreadedPlugin
from savu.plugins.utils import register_plugin

from i23.methods.segmentation import MASK_ITERATE

import numpy as np

@register_plugin
class MaskEvolve3d(Plugin, MultiThreadedPlugin):
    """
    Fast segmentation by evolving the given 3D mask, the mask must be given \
    precisely through the segmented object otherwise segmentation will be incorrect.

    :param threshold: important parameter to control mask propagation. Default: 0.001.
    :param method: evolve based on the mean in the mask (choose 0) or max intensity value as threshold (choose 1). Default: 1.
    :param iterations: The number of iterations. Default: 500.
    :param out_datasets: The default names . Default: ['MASK_EVOLVED'].
    """

    def __init__(self):
        super(MaskEvolve3d, self).__init__("MaskEvolve3d")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_3D', 'single')
        in_pData[1].plugin_data_setup('VOLUME_3D', 'single') # the initialisation (mask)

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup('VOLUME_3D', 'single')

    def pre_process(self):
        # extract given parameters
        self.threshold = self.parameters['threshold']
        self.iterations = self.parameters['iterations']
        self.method = self.parameters['method']

    def process_frames(self, data):
        input_temp = data[0]
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0
        if (np.sum(data[1]) > 0):
            mask_evolve = MASK_ITERATE(input_temp, data[1], self.threshold, self.iterations, self.method)
        else:
            mask_evolve = np.uint8(np.zeros(np.shape(data[0])))
        return mask_evolve

    def nInput_datasets(self):
        return 2
    def nOutput_datasets(self):
        return 1
