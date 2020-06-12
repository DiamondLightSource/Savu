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
.. module:: morph_proc
   :platform: Unix
   :synopsis: Wrapper around skimage morphology routines for 2D morphological processing of binary or grayscale datasets

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
# importing skimage functions
from skimage.morphology import *

@register_plugin
class MorphProc(Plugin, CpuPlugin):
    """
    A Plugin to perform morphological operations on grayscale images \
    (use: erosion, dilation, opening, closing) or binary images \
    (use: binary_erosion, binary_dilation, binary_opening, binary_closing)

    :param disk_radius:  The radius of the disk-shaped structuring element for morphology. Default: 5.
    :param morph_operation: The type of morphological operation. Default: 'binary_opening'.
    :param pattern: pattern to apply this to. Default: "VOLUME_XZ".
    """

    def __init__(self):
        super(MorphProc, self).__init__("MorphProc")

    def setup(self):

        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def pre_process(self):
        # extract given parameters
        self.disk_radius = self.parameters['disk_radius']
        self.morph_operation = self.parameters['morph_operation']
        self.selem = disk(self.disk_radius)

    def process_frames(self, data):
        # run morphological operations here:
        integerMax = np.max(data[0])
        if (np.sum(data[0]) > 0):
            morph_result = eval(self.morph_operation)(data[0], self.selem)
            morph_result = np.uint8(morph_result*integerMax)
        else:
            morph_result = np.uint8(np.zeros(np.shape(data[0])))
        return [morph_result]

    def nInput_datasets(self):
        return 1
    def nOutput_datasets(self):
        return 1
