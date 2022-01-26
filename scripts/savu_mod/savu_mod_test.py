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
.. module:: savu_mod_test
   :platform: Unix
   :synopsis: A command line tool for editing process lists

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""

import unittest

import savu.test.test_utils as tu
import scripts.savu_mod.savu_mod as sm

class SavuModTest(unittest.TestCase):
    def setUp(self):
        self.parser = sm.arg_parser(doc=True)
        # Required arguments below:
        # plugin number/name
        # parameter number/name
        # (optional) plugin index
        # new parameter value
        # process list file path

    def test_invalid_directory(self):
        parsed = self.parser.parse_args(
            [
                "1",
                "5",
                "0.3",
                tu.get_test_process_path("savu_mod/tomo_false.savu"),
            ]
        )
        with self.assertRaises(ValueError):
            content, content_modified = sm.modify_content(parsed)

    def test_valid_directory(self):
        parsed = self.parser.parse_args(
            [
                "1",
                "5",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        content, content_modified = sm.modify_content(parsed)

    def test_valid_parameter(self):
        parsed = self.parser.parse_args(
            [
                "1",
                "5",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        content, content_modified = sm.modify_content(parsed)

    def test_valid_parameter_1(self):
        parsed = self.parser.parse_args(
            [
                "2",
                "3",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        content, content_modified = sm.modify_content(parsed)

    def test_invalid_parameter(self):
        parsed = self.parser.parse_args(
            [
                "1",
                "95",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        with self.assertRaises(ValueError):
            content, content_modified = sm.modify_content(parsed)

    def test_plugin_and_index(self):
        # If a plugin number is used, then the index becomes irrelevant.
        # Is an error message needed?
        parsed = self.parser.parse_args(
            [
                "2",
                "5",
                "4",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        content, content_modified = sm.modify_content(parsed)

    def test_plugin_name_and_index(self):
        # If a plugin name is used, then the index can fail
        parsed = self.parser.parse_args(
            [
                "FresnelFilter",
                "2",
                "4",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        with self.assertRaises(IndexError):
            content, content_modified = sm.modify_content(parsed)

    def test_plugin_name_and_index_1(self):
        # Use a plugin name
        parsed = self.parser.parse_args(
            [
                "FresnelFilter",
                "1",
                "4",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        content, content_modified = sm.modify_content(parsed)

    def test_invalid_plugin(self):
        parsed = self.parser.parse_args(
            [
                "19",
                "5",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        with self.assertRaises(ValueError):
            content, content_modified = sm.modify_content(parsed)

    def test_valid_plugin(self):
        parsed = self.parser.parse_args(
            [
                "1",
                "5",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        content, content_modified = sm.modify_content(parsed)

    def test_invalid_value(self):
        parsed = self.parser.parse_args(
            [
                "1",
                "5",
                '[?""/=+]',
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        content, content_modified = sm.modify_content(parsed)
        self.assertFalse(content_modified)

    def test_valid_value(self):
        parsed = self.parser.parse_args(
            [
                "1",
                "5",
                "0.3",
                tu.get_test_process_path(
                    "savu_mod/tomo_savu_mod_example.savu"
                ),
            ]
        )
        content, content_modified = sm.modify_content(parsed)
