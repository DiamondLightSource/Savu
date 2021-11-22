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
.. module:: simulator_misalignment
   :platform: Unix
   :synopsis: randomly shifts each 2D projection in x-y direction using skimage

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from skimage import transform as tf

import random
import numpy as np

@register_plugin
class SimulatorMisalignment(Plugin, CpuPlugin):
    def __init__(self):
        super(SimulatorMisalignment, self).__init__('SimulatorMisalignment')

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())
        out_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())

    def process_frames(self, data):
        projection = data[0] # extract a projection
        random_shift_x = random.uniform(-self.parameters['shift_amplitude'],self.parameters['shift_amplitude'])  #generate a random floating point number
        random_shift_y = random.uniform(-self.parameters['shift_amplitude'],self.parameters['shift_amplitude'])  #generate a random floating point number

        tform = tf.SimilarityTransform(translation=(random_shift_x, random_shift_y))
        projection_shifted = tf.warp(projection, tform, order=5)

        return projection_shifted

    def get_max_frames(self):
        return 'single'

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
