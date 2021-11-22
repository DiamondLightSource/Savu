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
.. module:: testing_iterative_plugin2
   :platform: Unix
   :synopsis: Iterative plugin example
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.iterative_plugin import IterativePlugin


@register_plugin
class TestingIterativePlugin2(BaseFilter, IterativePlugin):
    """
    A plugin to test the iterative plugin driver
    """

    def __init__(self):
        super(TestingIterativePlugin2, self).\
            __init__("TestingIterativePlugin2")

    def pre_process(self):
        self.set_iterations(3)

    def process_frames(self, data):
        if self.get_iteration() == 0:
            return data[0]
        return data[0]

    def post_process(self):
        # option here to break out of the iterations
        # self.set_processing_complete()
        pass

    def setup(self):
        self.exp.log(self.name + " Start")

        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')

        out_dataset[0].create_dataset(in_dataset[0])
        self.clone_dataset(out_dataset[1], out_dataset[0])

        out_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[1].plugin_data_setup('SINOGRAM', 'single')

        # try replacing input dataset with the output dataset
        self.set_iteration_datasets(0, [in_dataset[0]], [out_dataset[0]])
        self.set_iteration_datasets(1, [out_dataset[0]], [out_dataset[1]])

        self.exp.log(self.name + " End")

    def nOutput_datasets(self):
        return 2

    def nClone_datasets(self):
        return 1
