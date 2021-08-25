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
.. module:: morph_snakes3D
   :platform: Unix
   :synopsis: 3D segmentation using Morphological Level Sets or active countours.

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.multi_threaded_plugin import MultiThreadedPlugin
from savu.plugins.utils import register_plugin

import numpy as np

# using Morphological snakes module from
# https://github.com/pmneila/morphsnakes
from morphsnakes import morphological_chan_vese

@register_plugin
class MorphSnakes3d(Plugin, MultiThreadedPlugin):


    def __init__(self):
        super(MorphSnakes3d, self).__init__("MorphSnakes3d")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()

        getall = ["VOLUME_XZ", "voxel_y"]
        in_pData[0].plugin_data_setup('VOLUME_3D', 'single', getall=getall)
        in_pData[1].plugin_data_setup('VOLUME_3D', 'single', getall=getall) # the initialisation (mask)

        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        out_pData[0].plugin_data_setup('VOLUME_3D', 'single', getall=getall)

    def pre_process(self):
        # extract given parameters
        self.lambda1 = self.parameters['lambda1']
        self.lambda2 = self.parameters['lambda2']
        self.smoothing = self.parameters['smoothing']
        self.iterations = self.parameters['iterations']

    def process_frames(self, data):
        # run MorphSnakes here:
        if (np.sum(data[1]) > 0):
            segment_result = morphological_chan_vese(data[0], iterations=self.iterations, lambda1=self.lambda1, lambda2=self.lambda2, init_level_set=data[1])
        else:
            segment_result = np.uint8(np.zeros(np.shape(data[0])))
        return [segment_result]

    def nInput_datasets(self):
        return 2
    def nOutput_datasets(self):
        return 1
