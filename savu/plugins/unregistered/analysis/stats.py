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
.. module:: stats
   :platform: Unix
   :synopsis: grabs a selection of statistics.

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>
"""
import logging
import numpy as np

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


#@register_plugin
class Stats(Plugin, CpuPlugin):

    def __init__(self):
        logging.debug("Starting the statistics")
        super(Stats, self).__init__("Stats")

    def process_frames(self, data):
        data = data[0]
        if 'max' in self.parameters['required_stats']:
            maximum = np.max(data)
            op = np.array([maximum])
        return op

    def post_process(self):
        out_datasets = self.get_out_datasets()
        in_meta_data = self.get_in_meta_data()[0]
        data = out_datasets[0].data
        if self.parameters['required_stats'] == 'max':
            maximum = np.max(data)
            in_meta_data.set('max', maximum)

    def get_max_frames(self):
        return 'single'

    def setup(self):
        self.exp.log(self.name + " Start")
        _in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters["direction"],
                                      self.get_max_frames())
        nFrames = in_pData[0].get_total_frames()
        axis_labels = ['frame.unit', 'max.unit']
        out_dataset[0].create_dataset(axis_labels=axis_labels,
                                      shape=(nFrames, 1),
                                      remove=True)

        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[0].plugin_data_setup("METADATA", self.get_max_frames())
