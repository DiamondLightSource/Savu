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
.. module:: base_filter
   :platform: Unix
   :synopsis: A base class for all standard filters

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin


class BaseFilter(Plugin):
    """
    A Plugin to apply a simple dark and flatfield correction to some
    raw timeseries data
    """

    def __init__(self, name="BaseFilter"):
        super(BaseFilter, self).__init__(name)

    def get_plugin_pattern(self):
        return 'PROJECTION'

    def raw_data(self):
        """ Return True if the output dataset should retain ImageKey/NoImageKey
        instances if they exist, i.e. keep the darks and flats
        NB. This is only available if out_dataset is created from an in_dataset
        """
        return False

    def setup(self):
        self.exp.log(self.name + " Start")
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        # copy all required information from in_dataset[0]
        # raw=True/False => output is still raw data (retain darks and flats)
        out_dataset[0].create_dataset(in_dataset[0], raw=self.raw_data())

        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()
        # set pattern_name and nframes to process for all datasets
        plugin_pattern = self.get_plugin_pattern()
        in_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())
        out_pData[0].plugin_data_setup(plugin_pattern, self.get_max_frames())

        self.exp.log(self.name + " End")

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'multiple'
