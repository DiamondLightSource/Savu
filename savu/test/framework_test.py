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
.. module:: framework_test
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
        self.plugin_list = [base_class_name]

    def test_pipeline(self):
        input_data = None
        output = None
        for plugin_name in self.plugin_list:
            plugin = pu.load_plugin(None, plugin_name)
            if plugin_name == base_class_name:
                self.assertRaises(NotImplementedError, plugin.process,
                                  "test", "test", 1, 1)
                continue

            # load appropriate data
            if input_data is None:
                input_data = tu.get_appropriate_input_data(plugin)[0]
                self.assertIsNotNone(input_data,
                                     "Cannot find appropriate test data")

            # generate somewhere for the data to go
            output = tu.get_appropriate_output_data(plugin, [input_data])[0]
            self.assertIsNotNone(output,
                                 "Cannot create appropriate test output")

            plugin.set_parameters(None)

            plugin.process(input_data, output, 1, 0)
            print("Output from plugin under test ( %s ) is in %s" %
                  (plugin.name, output.backing_file.filename))

            input_data.complete()
            input_data = output

        if output is not None:
            output.complete()


class SimpleReconstructionTest(PluginTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.timeseries_field_corrections",
                            "savu.plugins.simple_recon"]


class SimpleReconWithRawMedianFilteringTest(PluginTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.median_filter",
                            "savu.plugins.timeseries_field_corrections",
                            "savu.plugins.simple_recon"]


class SimpleReconWithProjectionMedianFilteringTest(PluginTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.timeseries_field_corrections",
                            "savu.plugins.median_filter",
                            "savu.plugins.simple_recon"]


class SimpleReconWithVolumeMedianFilteringTest(PluginTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.timeseries_field_corrections",
                            "savu.plugins.simple_recon",
                            "savu.plugins.median_filter"]


class SimpleReconWithMedianFilteringTest(PluginTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.median_filter",
                            "savu.plugins.timeseries_field_corrections",
                            "savu.plugins.median_filter",
                            "savu.plugins.simple_recon",
                            "savu.plugins.median_filter"]
if __name__ == "__main__":
    unittest.main()
