# -*- coding: utf-8 -*-
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
.. module:: base_correction
   :platform: Unix
   :synopsis: A base class for dark and flat field corrections

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin


class BaseCorrection(Plugin):

    def __init__(self, name='BaseCorrection'):
        super(BaseCorrection, self).__init__(name)

    def setup(self):
        """
        Initial setup of all datasets required as input and output to the
        plugin.  This method is called before the process method in the plugin
        chain.
        """
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # copy all required information from in_dataset[0]
        out_dataset[0].create_dataset(in_dataset[0])
        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()
        # set pattern_name and nframes to process for all datasets
        if 'pattern' in list(self.parameters.keys()):
            pattern = self.parameters['pattern']
        else:
            pattern = 'PROJECTION'

        in_pData[0].plugin_data_setup(pattern, self.get_max_frames())
        out_pData[0].plugin_data_setup(pattern, self.get_max_frames())

    def get_max_frames(self):
        return 'multiple'

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
