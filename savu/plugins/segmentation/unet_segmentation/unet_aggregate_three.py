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
.. module:: unet_aggregate_three
   :platform: Unix
   :synopsis: a plugin to amalgamate the output from unet apply.

.. moduleauthor:: Mark Basham <mark.basham@rfi.ac.uk>
"""

import logging
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

@register_plugin
class UnetAggregateThree(Plugin, CpuPlugin):

    def __init__(self):
        logging.debug("Starting Unet Aggregate three")
        super(UnetAggregateThree, self).__init__('UnetAggregateThree')

    def setup(self):
        logging.debug('setting up the Unet Aggregate three plugin')
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_meta_data = in_dataset[0].meta_data

        #patterns = in_dataset[0].patterns

        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        in_pData[1].plugin_data_setup(self.parameters['pattern'], 'single')
        in_pData[2].plugin_data_setup(self.parameters['pattern'], 'single')

        #FIXME This is not for the general case, just for testing i am removing the last dim, but should remove the probabiliteis one specifically!
        shape = in_dataset[0].data_info.get('shape')[:3]
        axis_labels = in_dataset[0].data_info.get('axis_labels')[:3]
        patterns = in_dataset[0].data_info.get('data_patterns')

        out_dataset[0].create_dataset(in_dataset[0],
                patterns=patterns,
                axis_labels=axis_labels,
                shape=tuple(shape))

        out_pData[0].plugin_data_setup('VOLUME_XY', 'single')

    def nInput_datasets(self):
        return 3

    def nOutput_datasets(self):
        return 1

    def pre_process(self):
        pass;

    def process_frames(self, data):
        combined = data[0][...] + data[1][...] + data[2][...]

        prediction = combined.argmax(3)

        return prediction

    def post_process(self):
        pass

