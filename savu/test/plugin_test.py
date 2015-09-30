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
from savu.plugins.plugin import Plugin


"""
.. module:: plugins_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest

from savu.test import test_utils as tu
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.core.plugin_runner import PluginRunner

base_class_name = "savu.plugins.plugin"


class PluginTest(unittest.TestCase):

    def setUp(self):
        self.plugin_name = base_class_name
        self.data_type = None

    def test_get_plugin(self):
        try :
            plugin = tu.load_class(self.plugin_name)
            self.assertIsNotNone(plugin)
        except ImportError as e:
            print("Failed to run plugin test as libraries not available (%s), "
                  "passing test" % (e))
            pass

#    @unittest.skip("This whole system has changed, so this test needs to be updated")
    def test_process(self):
        print "in the test process"

        try:
            plugin = tu.load_class(self.plugin_name)
            if self.plugin_name == base_class_name:
                self.assertRaises(NotImplementedError, plugin.process, "test", "test")
                return

            options = tu.set_experiment(self.data_type)
            tu.set_plugin_list(options, self.plugin_name)
            plugin_runner = PluginRunner(options)
            plugin_runner.run_plugin_list(options)
        
        except ImportError as e:
            print("Failed to run plugin test as libraries not available (%s), passing test" % (e))
            pass

    @unittest.skip("Originally added in the main framework - requires completion in testing.")
    def test_data_padding(self, in_data, out_data):
        """
        Checks the input and output data sets for padding and prints a warning
        if there is a chance an error has been made
        """
        # check if input and output data sets are/are not padded
        in_padding = False; out_padding = False
        for data in in_data:
            if data.padding is not None:
                in_padding = True
        
        for data in out_data:
            if data.padding is not None:
                out_padding = True
#
#        if (in_padding != out_padding) || ():
#            warnings.warn("Padding on in_datasets is " + str(in_padding) +
#                          " but on out_datasets is " + str(out_padding))

class CpuPluginWrapper(Plugin, CpuPlugin):

    def __init__(self):
        super(CpuPluginWrapper, self).__init__()
        self.data = None
        self.output = None
        self.processes = None
        self.process_number = None
        self.transport = Transport()

    def process(self, data, output, processes, process, transport):
        self.data = data
        self.output = output
        self.processes = processes
        self.process_number = process


class CpuPluginTest(unittest.TestCase):

    def setUp(self):
        self.plugin = None

    @unittest.skip("This whole system has changed, so this test needs to be updated")
    def test_run_plugin(self):
        self.plugin = CpuPluginWrapper()
        self.plugin.run_plugin("data", "out", ["CPU0"], 0)
        self.assertEqual(self.plugin.processes, ["CPU0"])
        self.assertEqual(self.plugin.process_number, 0)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_plugin("data", "out",
                                ["CPU0", "CPU1", "CPU2", "CPU3"], 0)
        self.assertEqual(self.plugin.processes,
                         ["CPU0", "CPU1", "CPU2", "CPU3"])
        self.assertEqual(self.plugin.process_number, 0)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_plugin("data", "out",
                                ["CPU0", "CPU1", "CPU2", "CPU3"], 1)
        self.assertEqual(self.plugin.processes,
                         ["CPU0", "CPU1", "CPU2", "CPU3"])
        self.assertEqual(self.plugin.process_number, 1)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_plugin("data", "out",
                                ["CPU0", "CPU1", "CPU2", "CPU3"], 3)
        self.assertEqual(self.plugin.processes,
                         ["CPU0", "CPU1", "CPU2", "CPU3"])
        self.assertEqual(self.plugin.process_number, 3)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_plugin("data", "out",
                                ["CPU0", "GPU0", "CPU1", "GPU1"], 0)
        self.assertEqual(self.plugin.processes, ["CPU0", "CPU1"])
        self.assertEqual(self.plugin.process_number, 0)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_plugin("data", "out",
                                ["CPU0", "GPU0", "CPU1", "GPU1"], 1)
        self.assertEqual(self.plugin.processes, None)
        self.assertEqual(self.plugin.process_number, None)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_plugin("data", "out",
                                ["CPU0", "GPU0", "CPU1", "GPU1"], 2)
        self.assertEqual(self.plugin.processes, ["CPU0", "CPU1"])
        self.assertEqual(self.plugin.process_number, 1)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_plugin("data", "out",
                                ["CPU0", "GPU0", "CPU1", "GPU1"], 3)
        self.assertEqual(self.plugin.processes, None)
        self.assertEqual(self.plugin.process_number, None)

    @unittest.skip("This whole system has changed, so this test needs to be updated")
    def test_run_cpu6_gpu2(self):
        all_procs = ["CPU0", "CPU1", "CPU2", "CPU3",
                     "CPU4", "CPU5", "GPU0", "GPU1"]
        cpu_procs = ["CPU0", "CPU1", "CPU2",
                     "CPU3", "CPU4", "CPU5"]

        for i in range(8):
            self.plugin = CpuPluginWrapper()
            self.plugin.run_plugin("data", "out", all_procs, i)
            if i < 6:
                self.assertEqual(self.plugin.processes, cpu_procs)
                self.assertEqual(self.plugin.process_number, i)
            else:
                self.assertEqual(self.plugin.processes, None)
                self.assertEqual(self.plugin.process_number, None)


class TimeseriesFieldCorrectionsTest(PluginTest):

    def setUp(self):
        self.data_type = 'tomoRaw'
        self.plugin_name = "savu.plugins.timeseries_field_corrections"


class MedianFilterTest(PluginTest):

    def setUp(self):
        self.data_type = 'tomo'
        self.plugin_name = "savu.plugins.median_filter"


class SimpleReconTest(PluginTest):

    def setUp(self):
        self.data_type = 'tomo'
        self.plugin_name = "savu.plugins.simple_recon"

if __name__ == "__main__":
    unittest.main()
