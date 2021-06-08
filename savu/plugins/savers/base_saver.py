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
.. module:: base_saver
   :platform: Unix
   :synopsis: A base class for all saver plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin

class BaseSaver(Plugin):
    def __init__(self, name="BaseSaver"):
        super(BaseSaver, self).__init__(name)
        self.frame = None

    def setup(self):
        in_pData = self.get_plugin_in_datasets()
        pattern = self.get_pattern()
        in_pData[0].plugin_data_setup(pattern, self.get_max_frames())

    def _get_group_name(self, name):
        nPlugin = self.exp.meta_data.get('nPlugin')
        plugin_dict = self.exp._get_collection()['plugin_dict'][nPlugin]
        return "%i-%s-%s" % (nPlugin, plugin_dict['name'], name)

    def get_pattern(self):
        return self.parameters['pattern']

    def get_frame(self):
        return self.frame

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 0

    def get_max_frames(self):
        return 'single'
