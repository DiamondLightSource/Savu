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
                              "test", "test", 1, 1)
            return
        # load appropriate data
        data = tu.get_appropriate_input_data(plugin)
        self.assertGreater(len(data), 0, "Cannot find appropriate test data")

        # generate somewehere for the data to go
        output = tu.get_appropriate_output_data(plugin, data)
        self.assertGreater(len(output), 0,
                           "Cannot create appropriate output data")

        for i in range(len(data)):
            plugin.process(data[i], output[i], 1, 0)
            print("Output from plugin under test ( %s ) is in %s" %
                  (plugin.name, output[i].backing_file.filename))

            data[i].complete()
            output[i].complete()


class TimeseriesFieldCorrectionsTest(PluginTest):

    def setUp(self):
        self.plugin_name = "savu.plugins.timeseries_field_corrections"


class Median3x3FilterTest(PluginTest):

    def setUp(self):
        self.plugin_name = "savu.plugins.median_3x3_filter"


class SimpleReconTest(PluginTest):

    def setUp(self):
        self.plugin_name = "savu.plugins.simple_recon"

if __name__ == "__main__":
    unittest.main()
