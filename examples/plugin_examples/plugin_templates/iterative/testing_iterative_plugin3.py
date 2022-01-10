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
.. module:: testing_iterative_plugin3
   :platform: Unix
   :synopsis: Iterative plugin example
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.iterative_plugin import IterativePlugin


@register_plugin
class TestingIterativePlugin3(BaseFilter, IterativePlugin):
    """
    A plugin to test the iterative plugin driver
    """

    def __init__(self):
        super(TestingIterativePlugin3, self).\
            __init__("TestingIterativePlugin3")

    def pre_process(self):
        self.set_iterations(3)

    def process_frames(self, data):
        return [data[0], data[0]]

    def post_process(self):
        # option here to break out of the iterations
        # self.set_processing_complete()
        pass

    def setup(self):
        self.exp.log(self.name + " Start")

        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())

        # these are the datasets with names
        out_dataset[0].create_dataset(in_dataset[0])
        out_dataset[1].create_dataset(in_dataset[0])
        # these are the clones
        out_dataset[2].create_dataset(out_dataset[0])
        out_dataset[3].create_dataset(out_dataset[1])

        out_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[1].plugin_data_setup('SINOGRAM', 'single')
        out_pData[2].plugin_data_setup('SINOGRAM', 'single')
        out_pData[3].plugin_data_setup('SINOGRAM', 'single')

        # try replacing input dataset with the output dataset
        dIn = [in_dataset[0]]
        dOut = [out_dataset[0], out_dataset[1]]
        self.set_iteration_datasets(0, dIn, dOut)

        dIn = [out_dataset[0], out_dataset[0], out_dataset[1]]
        dOut = [out_dataset[2], out_dataset[3]]
        self.set_iteration_datasets(1, dIn, dOut)

        # cloned datasets used as alternating datasets?
        self.set_alternating_datasets(out_dataset[0], out_dataset[2])
        self.set_alternating_datasets(out_dataset[1], out_dataset[3])

        self.exp.log(self.name + " End")

    def nOutput_datasets(self):
        return 4

    def nClone_datasets(self):
        return 2
