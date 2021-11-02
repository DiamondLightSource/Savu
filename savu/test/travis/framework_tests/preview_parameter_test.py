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
        ppath = "savu.test.travis.framework_tests.no_process"
        plugin = pu.load_class(ppath)()
        plugin_tools = plugin.get_plugin_tools()
        plugin_tools._populate_default_parameters()
        pdefs = plugin_tools.get_param_definitions()
        return pdefs

    def check_modification(self, value, key, pdefs):
        """
        Convert the value to it's correct type
        Check if this value is a valid dtype for that parameter
        """
        value_check = pu._dumps(value)
        valid_modification, error_str = \
            param_u.is_valid(key, value_check, pdefs[key])
        return valid_modification

    def test_1(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [9]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_2(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [9,8,89]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_3(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [9,"8:9"]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_4(self):
        # Check that list is accepted (string format)
        pdefs = self.initial_setup()
        key = "preview"
        value = "[7,9]"
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_5(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [9, 'mid']
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_6(self):
        # Check that list with keyword is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = ['9+mid', 'mid+40', 90]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_7(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [':9','::3', 9]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_8(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [9, '8:87:3', 8]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_9(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = []
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_10(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [3,4,5,6]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_11(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = ['5:9:1','6:90:2','7:5:1']
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_12(self):
        # Check that list with string letter is not accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = ['a5:9:1','6:90:2','7:5:1']
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_13(self):
        # Check that list with blank is not accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = ['','6:90:2','7:5:1']
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_14(self):
        # Check that list is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [':','6:90:2','7:5:1']
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_15(self):
        # Check that list with default ::: start stop step is accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [':::','6:90:2','7:5:1']
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_16(self):
        # Check that three colons are accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [':9::','6:90:2','7:5:1']
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_17(self):
        # Check that multiple colons are not accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [':9::','6:90:2:::','7:5:1']
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_18(self):
        # Check that spaces are not affected/accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [':', ':', '12 : -34']
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_19(self):
        # Check that symbols are accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = [':', ':', '12:-34']
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_20(self):
        # Check that key words and symbols are accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = ['mid - 1:mid + 1', ':', '12']
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_21(self):
        # Check that key words and incorrect letters are not accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = ['another - 1:mid + 1', ':', '12']
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_22(self):
        # Check that key words and incorrect letters are not accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = ['another - 1: 1', ':', '12']
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_23(self):
        # Check that key word letters in incorrect order are not accepted
        pdefs = self.initial_setup()
        key = "preview"
        value = ['dim - 1: 1', ':', '12']
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_24(self):
        # Check that boolean False is declined
        pdefs = self.initial_setup()
        key = "preview"
        value = False
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_25(self):
        # Check that boolean True is declined
        pdefs = self.initial_setup()
        key = "preview"
        value = True
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_26(self):
        # Check that boolean True is declined
        pdefs = self.initial_setup()
        key = "preview"
        value = "another input"
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_27(self):
        # Check that boolean True is declined
        pdefs = self.initial_setup()
        key = "preview"
        value = 5
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_28(self):
        # Check that empty dict is declined
        pdefs = self.initial_setup()
        key = "preview"
        value = {}
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_29(self):
        # Check that comma string is declined
        pdefs = self.initial_setup()
        key = "preview"
        value = ":,:,:"
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_30(self):
        # Check that comma string list is declined
        pdefs = self.initial_setup()
        key = "preview"
        value = [":,:,:"]
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_31(self):
        # Check that punctuation is declined
        pdefs = self.initial_setup()

        import string
        for x in string.punctuation:
            if x != ":":
                key = "preview"
                value = [x]
                self.assertFalse(self.check_modification(value, key, pdefs))

    def test_32(self):
        # Check that slice notation and punctuation is declined
        pdefs = self.initial_setup()

        import string
        for x in string.punctuation:
            if x != ":":
                key = "preview"
                value = [f"{x}:"]
                self.assertFalse(self.check_modification(value, key, pdefs))

    def test_33(self):
        # Check that default list : is allowed
        pdefs = self.initial_setup()

        key = "preview"
        value = [":"]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_34(self):
        # Check that start keyword is allowed
        pdefs = self.initial_setup()

        key = "preview"
        value = ["start:65"]
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_dict_1(self):
        # Check that key value dict is not accepted if preview is invalid
        pdefs = self.initial_setup()
        key = "savu_nexus_preview"
        value = {"data":['dim - 1: 1', ':', '12']}
        self.assertFalse(self.check_modification(value, key, pdefs))

    def test_dict_2(self):
        # Check that empty dict is accepted
        pdefs = self.initial_setup()
        key = "savu_nexus_preview"
        value = {}
        self.assertTrue(self.check_modification(value, key, pdefs))

    def test_dict_3(self):
        # Check that key value dict is accepted
        pdefs = self.initial_setup()
        key = "savu_nexus_preview"
        value = {"data":['mid - 1: 1', ':', '12']}
        self.assertTrue(self.check_modification(value, key, pdefs))

if __name__ == "__main__":
    unittest.main()
