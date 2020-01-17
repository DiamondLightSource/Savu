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

import savu
import os

from savu.plugins import utils as pu
from savu.plugins import docstring_parser as doc
from savu.plugins import plugin as test_plugin


class Test(unittest.TestCase):

    def testGetPlugin(self):
        plugin = pu.get_plugin("savu.plugins.plugin")
        self.assertEqual(plugin.__class__, test_plugin.Plugin,
                         "Failed to load the correct class")
        self.assertRaises(NotImplementedError,
                          plugin.process_frames, None)

    def testfind_args(self):
        plugin = pu.get_plugin("savu.plugins.filters.denoising.denoise_bregman_filter")
        params = doc.find_args(plugin)
        self.assertEqual(len(params['param']), 4)

    def test_get_plugin_external_path(self):
        savu_path = os.path.split(savu.__path__[0])[0]
        plugin = pu.get_plugin(os.path.join(savu_path, "plugin_examples",
                                            "example_median_filter.py"))
        self.assertEqual(plugin.name, "ExampleMedianFilter")

    def test_get_plugins_paths(self):
        n_paths = len(pu.get_plugins_paths())
        os.environ["SAVU_PLUGINS_PATH"] = "/tmp/"
        paths = pu.get_plugins_paths()
        self.assertEqual(len(paths), n_paths+1)
        os.environ["SAVU_PLUGINS_PATH"] = ""

    def test_get_plugins_paths2(self):
        n_paths = len(pu.get_plugins_paths())
        os.environ["SAVU_PLUGINS_PATH"] = "/tmp/:/dev/:/home/"
        paths = pu.get_plugins_paths()
        self.assertEqual(len(paths), n_paths+3)
        os.environ["SAVU_PLUGINS_PATH"] = ""

    def test_get_plugins_path_and_load(self):
        savu_path = os.path.split(savu.__path__[0])[0]
        plugin_path = os.path.join(savu_path, "plugin_examples")
        os.environ["SAVU_PLUGINS_PATH"] = plugin_path
        pu.get_plugins_paths()
        plugin = pu.get_plugin("example_median_filter")
        self.assertEqual(plugin.name, "ExampleMedianFilter")
        os.environ["SAVU_PLUGINS_PATH"] = ""

if __name__ == "__main__":
    unittest.main()
