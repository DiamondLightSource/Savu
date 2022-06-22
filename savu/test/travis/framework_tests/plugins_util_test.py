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
from savu.plugins import plugin as test_plugin


class PluginsUtilTest(unittest.TestCase):
    def testGetPlugin(self):
        mod = "savu.plugins.plugin"
        plugin = pu.load_class(mod)()
        self.assertEqual(
            plugin.__class__,
            test_plugin.Plugin,
            "Failed to load the correct class",
        )
        self.assertRaises(NotImplementedError, plugin.process_frames, None)

    def test_get_plugin_external_path(self):
        savu_path = os.path.split(savu.__path__[0])[0]
        mod = os.path.join(
            savu_path, "examples/plugin_examples", "example_median_filter.py"
        )
        pu.get_plugins_paths()
        plugin = pu.load_class(mod)()
        self.assertEqual(plugin.name, "ExampleMedianFilter")

    def _add_to_plugins_path(self, add_paths):
        env = "SAVU_PLUGINS_PATH"
        path = os.environ[env] if env in os.environ.keys() else ""
        os.environ[env] = ":".join([path, add_paths])

    def test_get_plugins_paths(self):
        n_paths = len(pu.get_plugins_paths())
        self._add_to_plugins_path("/tmp")
        paths = pu.get_plugins_paths()
        self.assertEqual(len(paths), n_paths + 1)

    def test_get_plugins_paths2(self):
        n_paths = len(pu.get_plugins_paths())
        self._add_to_plugins_path("/tmp/:/dev/:/home/")
        paths = pu.get_plugins_paths()
        self.assertEqual(len(paths), n_paths + 3)

    def test_get_plugins_path_and_load(self):
        savu_path = os.path.split(savu.__path__[0])[0]
        plugin_path = os.path.join(savu_path, "examples/plugin_examples")
        os.environ["SAVU_PLUGINS_PATH"] = plugin_path
        pu.get_plugins_paths()
        plugin = pu.load_class("example_median_filter")()
        self.assertEqual(plugin.name, "ExampleMedianFilter")
        os.environ["SAVU_PLUGINS_PATH"] = ""

    def test_get_tools_class(self):
        mod = "savu.plugins.filters.denoising.denoise_bregman_filter_tools"
        tools_class = pu.get_tools_class(mod)
        self.assertEqual(tools_class.__name__, "DenoiseBregmanFilterTools")

    def test_param_to_str(self):
        """Check a parameter name is returned as a str"""
        param = "angles"
        param_key_list = ['preview', 'data_path', 'dark', 'flat', 'name',
                          'image_key_path', 'angles', '3d_to_4d', 'ignore_flats']
        param_name = pu.param_to_str(param, param_key_list)
        self.assertEqual(param_name, "angles")

    def test_param_to_str_1(self):
        """Check a parameter number is returned as a str"""
        param = "7"
        param_key_list = ['preview', 'data_path', 'dark', 'flat', 'name',
                          'image_key_path', 'angles', '3d_to_4d', 'ignore_flats']
        param_name = pu.param_to_str(param, param_key_list)
        self.assertEqual(param_name, "angles")

    def test_param_to_str_2(self):
        """Check an error is returned if parameter number is invalid"""
        param = "10"
        param_key_list = ['preview', 'data_path', 'dark', 'flat', 'name',
                          'image_key_path', 'angles', '3d_to_4d', 'ignore_flats']
        with self.assertRaises(Exception):
            param_name = pu.param_to_str(param, param_key_list)

    def test_param_to_str_3(self):
        """Check an error is returned if parameter number is invalid"""
        param = "12"
        param_key_list = ['preview', 'data_path', 'dark', 'flat', 'name',
                          'image_key_path', 'angles', '3d_to_4d', 'ignore_flats']
        with self.assertRaises(ValueError):
            param_name = pu.param_to_str(param, param_key_list)

    def test_param_to_str_4(self):
        """Check an error is returned if parameter name is invalid"""
        param = "angletrait"
        param_key_list = ['preview', 'data_path', 'dark', 'flat', 'name',
                          'image_key_path', 'angles', '3d_to_4d', 'ignore_flats']
        with self.assertRaises(Exception):
            param_name = pu.param_to_str(param, param_key_list)

    def test_sort_alphanum(self):
        """Sort list numerically and alphabetically
        *While maintaining original list value types*
        """
        num_list = ["3", "5", "4", "6"]
        sorted_list = pu.sort_alphanum(num_list)
        self.assertEqual(sorted_list, ["3", "4", "5", "6"])

    def test_sort_alphanum_1(self):
        """Sort list numerically and alphabetically
        *While maintaining original list value types*
        """
        num_list = ["  3", "  5", "  4", "  6"]
        sorted_list = pu.sort_alphanum(num_list)
        self.assertEqual(sorted_list, ["  3", "  4", "  5", "  6"])

    def test_sort_alphanum_2(self):
        """Sort list numerically and alphabetically
        *While maintaining original list value types*
        """
        num_list = ["  3", "  5", "  4a", "  6"]
        sorted_list = pu.sort_alphanum(num_list)
        self.assertEqual(sorted_list, ["  3", "  4a", "  5", "  6"])

    def test_sort_alphanum_3(self):
        """Sort list numerically and alphabetically
        *While maintaining original list value types*
        """
        num_list = ["  3", "  4c", "  4a", "  4b"]
        sorted_list = pu.sort_alphanum(num_list)
        self.assertEqual(sorted_list, ["  3", "  4a", "  4b", "  4c"])

    def test_sort_alphanum_4(self):
        """Sort list numerically and alphabetically
        *While maintaining original list value types*
        """
        num_list = ["3", "5", "4", "6", "7", "8", "9", "10", "11", "12"]
        sorted_list = pu.sort_alphanum(num_list)
        self.assertEqual(
            sorted_list, ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        )

    def test_sort_alphanum_5(self):
        """Sort list numerically and alphabetically
        *While maintaining original list value types*
        """
        num_list = ["13", "5", "4", "6", "7", "8", "9", "10", "11", "12"]
        sorted_list = pu.sort_alphanum(num_list)
        self.assertEqual(
            sorted_list,
            ["4", "5", "6", "7", "8", "9", "10", "11", "12", "13"],
        )

    def test__alphanum(self):
        """Split string into numbers and letters"""
        alpha_str = "4b"
        alpha_list = pu._alphanum(alpha_str)
        self.assertEqual(alpha_list, [4, "b"])

    def test__alphanum_1(self):
        """Split string into numbers and letters"""
        alpha_str = "    4b"
        alpha_list = pu._alphanum(alpha_str)
        self.assertEqual(alpha_list, [4, "b"])

    def test__alphanum_2(self):
        """Split string into numbers and letters"""
        alpha_str = "    4"
        alpha_list = pu._alphanum(alpha_str)
        self.assertEqual(alpha_list, [4])

    def test__alphanum_3(self):
        """Split string into numbers and letters"""
        alpha_str = "4"
        alpha_list = pu._alphanum(alpha_str)
        self.assertEqual(alpha_list, [4])

    def test__str_to_int(self):
        """If the string is a digit, then convert to int type
        Otherwise keep as string type"""
        _str = "4"
        _int = pu._str_to_int(_str)
        self.assertEqual(_int, 4)

    def test__str_to_int_1(self):
        """If the string is a digit, then convert to int type
        Otherwise keep as string type"""
        _str = "a"
        _int = pu._str_to_int(_str)
        self.assertEqual(_int, "a")


if __name__ == "__main__":
    unittest.main()
