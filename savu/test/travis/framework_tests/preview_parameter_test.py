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

"""
.. module:: preview_parameter_test
   :platform: Unix
   :synopsis: unittest test for preview parameter
.. moduleauthor:: Jessica Verschoyle <jessica.verschoyle@diamond.ac.uk>

"""

import unittest

import savu.plugins.utils as pu
import scripts.config_generator.parameter_utils as param_u


class PreviewParameterTest(unittest.TestCase):
    def initial_setup(self):
        ppath = "savu.plugins.basic_operations.no_process"
        plugin = pu.load_class(ppath)()
        plugin._populate_default_parameters()
        return plugin

    def test_1(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [9]
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_2(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [9,8,89]
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_3(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [9,"8:9"]
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_4(self):
        # Check that list is accepted (string format)
        plugin = self.initial_setup()
        key = "preview"
        value = "[7,9]"
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_5(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [9, 'mid']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_6(self):
        # Check that list with keyword is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = ['9+mid', 'mid+40', 90]
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_7(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [':9','::3', 9]
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_8(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [9, '8:87:3', 8]
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_9(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = []
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_10(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [3,4,5,6]
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_11(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = ['5:9:1','6:90:2','7:5:1']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_12(self):
        # Check that list with string letter is not accepted
        plugin = self.initial_setup()
        key = "preview"
        value = ['a5:9:1','6:90:2','7:5:1']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_13(self):
        # Check that list with blank is not accepted
        plugin = self.initial_setup()
        key = "preview"
        value = ['','6:90:2','7:5:1']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_14(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [':','6:90:2','7:5:1']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_15(self):
        # Check that list with default ::: start stop step is accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [':::','6:90:2','7:5:1']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_16(self):
        # Check that three colons are accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [':9::','6:90:2','7:5:1']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_17(self):
        # Check that multiple colons are not accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [':9::','6:90:2:::','7:5:1']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_18(self):
        # Check that spaces are not affected/accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [':', ':', '12 : -34']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_19(self):
        # Check that symbols are accepted
        plugin = self.initial_setup()
        key = "preview"
        value = [':', ':', '12:-34']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_20(self):
        # Check that key words and symbols are accepted
        plugin = self.initial_setup()
        key = "preview"
        value = ['mid - 1:mid + 1', ':', '12']
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

if __name__ == "__main__":
    unittest.main()
