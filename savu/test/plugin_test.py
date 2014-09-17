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
.. module:: plugins_util_test
   :platform: Unix
   :synopsis: unittest test class for plugin utils

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest

from savu.plugins import utils as pu
from savu.test import test_utils as tu

base_class_name = "savu.plugins.plugin"


class PluginTest(unittest.TestCase):

    def setUp(self):
        self.plugin_name = base_class_name

    def test_get_plugin(self):
        plugin = pu.load_plugin(None, self.plugin_name)
        self.assertIsNotNone(plugin)

    def test_process(self):
        plugin = pu.load_plugin(None, self.plugin_name)
        if self.plugin_name == base_class_name:
            self.assertRaises(NotImplementedError, plugin.process,
                              "test", 1, 1)
            return
        # get the data
        data = tu.get_nexus_test_data()
        plugin.process(data, 1, 0)


class TimeseriesFieldCorrectionsTest(PluginTest):

    def setUp(self):
        self.plugin_name = "savu.plugins.timeseries_field_corrections"


if __name__ == "__main__":
    unittest.main()
