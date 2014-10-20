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

from savu.plugins import utils as pu
from savu.test import test_utils as tu
from savu.plugins.cpu_plugin import CpuPlugin

base_class_name = "savu.plugins.plugin"


class PluginTest(unittest.TestCase):

    def setUp(self):
        self.plugin_name = base_class_name

    def test_get_plugin(self):
        plugin = pu.load_plugin(self.plugin_name)
        self.assertIsNotNone(plugin)

    def test_process(self):
        plugin = pu.load_plugin(self.plugin_name)
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

        plugin.set_parameters(None)

        for i in range(len(data)):
            plugin.run_process(data[i], output[i], "CPU0", 0)
            print("Output from plugin under test ( %s ) is in %s" %
                  (plugin.name, output[i].backing_file.filename))

            data[i].complete()
            output[i].complete()


class CpuPluginWrapper(Plugin, CpuPlugin):

    def __init__(self):
        super(CpuPluginWrapper, self).__init__()
        self.data = None
        self.output = None
        self.processes = None
        self.process_number = None

    def process(self, data, output, processes, process):
        self.data = data
        self.output = output
        self.processes = processes
        self.process_number = process


class CpuPluginTest(unittest.TestCase):

    def setUp(self):
        self.plugin = None

    def test_run_process(self):
        self.plugin = CpuPluginWrapper()
        self.plugin.run_process("data", "out", ["CPU0"], 0)
        self.assertEqual(self.plugin.processes, ["CPU0"])
        self.assertEqual(self.plugin.process_number, 0)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_process("data", "out",
                                ["CPU0", "CPU1", "CPU2", "CPU3"], 0)
        self.assertEqual(self.plugin.processes,
                         ["CPU0", "CPU1", "CPU2", "CPU3"])
        self.assertEqual(self.plugin.process_number, 0)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_process("data", "out",
                                ["CPU0", "CPU1", "CPU2", "CPU3"], 1)
        self.assertEqual(self.plugin.processes,
                         ["CPU0", "CPU1", "CPU2", "CPU3"])
        self.assertEqual(self.plugin.process_number, 1)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_process("data", "out",
                                ["CPU0", "CPU1", "CPU2", "CPU3"], 3)
        self.assertEqual(self.plugin.processes,
                         ["CPU0", "CPU1", "CPU2", "CPU3"])
        self.assertEqual(self.plugin.process_number, 3)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_process("data", "out",
                                ["CPU0", "GPU0", "CPU1", "GPU1"], 0)
        self.assertEqual(self.plugin.processes, ["CPU0", "CPU1"])
        self.assertEqual(self.plugin.process_number, 0)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_process("data", "out",
                                ["CPU0", "GPU0", "CPU1", "GPU1"], 1)
        self.assertEqual(self.plugin.processes, None)
        self.assertEqual(self.plugin.process_number, None)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_process("data", "out",
                                ["CPU0", "GPU0", "CPU1", "GPU1"], 2)
        self.assertEqual(self.plugin.processes, ["CPU0", "CPU1"])
        self.assertEqual(self.plugin.process_number, 1)

        self.plugin = CpuPluginWrapper()
        self.plugin.run_process("data", "out",
                                ["CPU0", "GPU0", "CPU1", "GPU1"], 3)
        self.assertEqual(self.plugin.processes, None)
        self.assertEqual(self.plugin.process_number, None)

    def test_run_cpu6_gpu2(self):
        all_procs = ["CPU0", "CPU1", "CPU2", "CPU3",
                     "CPU4", "CPU5", "GPU0", "GPU1"]
        cpu_procs = ["CPU0", "CPU1", "CPU2",
                     "CPU3", "CPU4", "CPU5"]

        for i in range(8):
            self.plugin = CpuPluginWrapper()
            self.plugin.run_process("data", "out", all_procs, i)
            if i < 6:
                self.assertEqual(self.plugin.processes, cpu_procs)
                self.assertEqual(self.plugin.process_number, i)
            else:
                self.assertEqual(self.plugin.processes, None)
                self.assertEqual(self.plugin.process_number, None)


class TimeseriesFieldCorrectionsTest(PluginTest):

    def setUp(self):
        self.plugin_name = "savu.plugins.timeseries_field_corrections"


class MedianFilterTest(PluginTest):

    def setUp(self):
        self.plugin_name = "savu.plugins.median_filter"


class SimpleReconTest(PluginTest):

    def setUp(self):
        self.plugin_name = "savu.plugins.simple_recon"

if __name__ == "__main__":
    unittest.main()
