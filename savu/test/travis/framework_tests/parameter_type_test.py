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
.. module:: parameter_type_test
   :platform: Unix
   :synopsis: unittest test for plugin parameter data types
.. moduleauthor:: Jessica Verschoyle <jessica.verschoyle@diamond.ac.uk>

"""

import unittest

import savu.plugins.utils as pu
import scripts.config_generator.parameter_utils as param_u


class ParameterTypeTest(unittest.TestCase):
    def initial_setup(self):
        ppath = "savu.plugins.basic_operations.no_process"
        plugin = pu.load_class(ppath)()
        plugin._populate_default_parameters()
        return plugin

    def test_int(self):
        # Check that integer is accepted
        plugin = self.initial_setup()
        key = "int_param"
        value = 7
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_1(self):
        # Check that string is declined
        plugin = self.initial_setup()
        key = "int_param"
        value = "hello"
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_2(self):
        # Float value is declined
        plugin = self.initial_setup()
        key = "int_param"
        value = 7.0
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_3(self):
        # Octal value not converted
        '''If your YAML contains integer values that start with a 0 and do not
        contain digits greater than 7, they will be parsed as octal values.'''
        plugin = self.initial_setup()
        key = "int_param"
        value = "0123"
        value_check = pu._dumps(value)
        self.assertEqual("0123", value_check)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_4(self):
        # Sexagesimal value not converted to integer
        # sexagesimal and the 9:00 is considered to be similar to 9 minutes and 0 seconds, equalling a total of 540 seconds.
        plugin = self.initial_setup()
        key = "int_param"
        value = "9:00"
        value_check = pu._dumps(value)
        self.assertEqual(value_check, '9:00')
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_5(self):
        # Boolean value not converted to integer
        plugin = self.initial_setup()
        key = "int_param"
        value = "True"
        value_check = pu._dumps(value)
        self.assertEqual(value_check, True)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_float(self):
        # Check that string is declined
        plugin = self.initial_setup()
        key = "float_param"
        value = "hello"
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_float_1(self):
        # Int value is accepted
        plugin = self.initial_setup()
        key = "float_param"
        value = 7
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_float_2(self):
        # Float value is accepted
        plugin = self.initial_setup()
        key = "float_param"
        value = 7.99
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_float_3(self):
        # Sexagesimal value not converted to integer
        # sexagesimal and the 9:00 is considered to be similar to 9 minutes and 0 seconds, equalling a total of 540 seconds.
        plugin = self.initial_setup()
        key = "float_param"
        value = "9:00"
        value_check = pu._dumps(value)
        self.assertEqual(value_check, '9:00')
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_float_4(self):
        # Boolean value not converted to integer
        plugin = self.initial_setup()
        key = "float_param"
        value = "True"
        value_check = pu._dumps(value)
        self.assertEqual(value_check, True)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_yaml(self):
        # Check that yaml file is accepted (this value is also the default)
        plugin = self.initial_setup()
        key = "yaml_file"
        value = "savu/plugins/loaders/full_field_loaders/nxtomo_loader.yaml"
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_yaml_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "yaml_file"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_yaml_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = "yaml_file"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_yaml_3(self):
        # Check that yaml file is accepted
        plugin = self.initial_setup()
        key = "yaml_file"
        value = "savu/plugins/loaders/templates/nexus_templates/fluo.yml"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_yaml_4(self):
        # Check that incorrect yaml file is not accepted
        plugin = self.initial_setup()
        key = "yaml_file"
        value = "savu/plugins/loaders/templates/nexus_templates/nxtomo_loader_incorrect.yaml"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_yaml_5(self):
        # Check that yaml file is accepted
        plugin = self.initial_setup()
        key = "yaml_file"
        value = "savu/plugins/loaders/templates/nexus_templates/mm.yml"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_file_path(self):
        # Check that filepath is accepted
        plugin = self.initial_setup()
        key = "file_path_param"

        import os
        savu_base_path = \
            os.path.dirname(os.path.realpath(__file__)).split('savu')[0]

        value = savu_base_path + "system_files/dls/test_dev_script.txt"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_file_path_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "file_path_param"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_file_path_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = "file_path_param"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_file_path_3(self):
        # Check that yaml filepath is accepted
        plugin = self.initial_setup()
        key = "file_path_param"
        value = "savu/plugins/loaders/templates/nexus_templates/fluo.yml"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_file_path_4(self):
        # Check that incorrect filepath is not accepted
        plugin = self.initial_setup()
        key = "file_path_param"
        value = "savu/plugins/loaders/templates/nexus_templates/nxtomo_loader_incorrect.yaml"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string(self):
        # Check that string is accepted
        plugin = self.initial_setup()
        key = "pattern"
        value = "An example"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_string_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "pattern"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = "pattern"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_3(self):
        # Check that None as a string is accepted
        plugin = self.initial_setup()
        key = "pattern"
        value = 'None'

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_tuple(self):
        # Check that tuple is accepted
        plugin = self.initial_setup()
        key = "vocentering_search_area"
        value = (1, 2)

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_tuple_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "vocentering_search_area"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_tuple_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = "vocentering_search_area"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_tuple_3(self):
        # Check that list is not accepted (string format)
        plugin = self.initial_setup()
        key = "vocentering_search_area"
        value = "[2, 3, 4, 5]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_tuple_4(self):
        # Check that tuple is accepted (string format)
        plugin = self.initial_setup()
        key = "vocentering_search_area"
        value = "(1, 2)"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_list(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = "Testing str"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_list_3(self):
        # Check that list is accepted (string format)
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = "[2, 3, 4, 5]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_list_4(self):
        # Check that str list is accepted (string format)
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = "[one,two,three]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_list_5(self):
        # Check that str list is accepted
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = ['one', 'two', 'three']

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_list_6(self):
        # Check that str list is accepted
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = ['A longer sentence', 'two', 'three']

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_list_7(self):
        # Check that empty list is rejected
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = []

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_empty_list(self):
        # Check that int list is not accepted
        plugin = self.initial_setup()
        key = "empty_list_param"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_empty_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "empty_list_param"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_empty_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = "empty_list_param"
        value = "Testing str"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_empty_list_3(self):
        # Check that str list is not accepted
        plugin = self.initial_setup()
        key = "empty_list_param"
        value = ["value", "second6"]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_empty_list_4(self):
        # Check that empty list is accepted
        plugin = self.initial_setup()
        key = "empty_list_param"
        value = []

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_empty_list_5(self):
        # Check that empty list is accepted (string format)
        plugin = self.initial_setup()
        key = "empty_list_param"
        value = "[]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_list(self):
        # Check that int list is accepted
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = "Testing str"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_list_3(self):
        # Check that str list is not accepted
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = ["value", "second6"]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_list_4(self):
        # Check that int list is accepted (string format)
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = "[3,7,8]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_list_5(self):
        # Check that str list is not accepted (string format)
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = "[value, second6]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_list_6(self):
        # Check that str of numbers is not accepted
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = "6 8 9"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_list_7(self):
        # Check that str list is not accepted (string format)
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = "[6:0, 9:8]"

        value_check = pu._dumps(value)
        self.assertEqual(['6:0', '9:8'], value_check)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_list_8(self):
        # Check that str list is not accepted
        plugin = self.initial_setup()
        key = "integer_list_param"
        value = ['6:0', '9:8']

        value_check = pu._dumps(value)
        self.assertEqual(['6:0', '9:8'], value_check)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_list(self):
        # Check that string list is accepted
        plugin = self.initial_setup()
        key = "string_list_param"
        value = ["value", "second6"]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_string_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "string_list_param"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "Testing str with multiple words"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_list_3(self):
        # Check that int list is not accepted
        plugin = self.initial_setup()
        key = "string_list_param"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_list_4(self):
        # Check that string list without quotes is accepted
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "[another, example]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_string_list_5(self):
        # Check that mixed list without quotes is declined
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "[another, 5, 8.0]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_list_6(self):
        # Check that string is declined
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "example"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_list_7(self):
        # Check that multiple integers inside a string are declined
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "4 6 7 86"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_list_8(self):
        # Check that string list in string format is accepted
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "['one','two']"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_string_list_9(self):
        # Check that empty list is rejected
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "[]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_string_list_10(self):
        # Check that string list is accepted
        plugin = self.initial_setup()
        key = "string_list_param"
        value = ['5:600']

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_string_list_11(self):
        # Check that string list is accepted (string format)
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "[5:600]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_string_list_12(self):
        # Check that string list is accepted (string format)
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "[5:600,5:7]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_string_list_13(self):
        # Check that string list is accepted (string format)
        # Previously sexigesimal values could be changed to int if yaml.load is used
        plugin = self.initial_setup()
        key = "string_list_param"
        value = "[5:600,5:7]"
        value_check = pu._dumps(value)
        self.assertEqual(value_check, ['5:600','5:7'])
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_num_list(self):
        # Check that int list is accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_num_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_num_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = "Testing str"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_num_list_3(self):
        # Check that str list is not accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = ["value", "second6"]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_num_list_4(self):
        # Check that float and int list is accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = [10.4, 30.6, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_num_list_5(self):
        # Check that float only list is accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = [10.4, 30.6, 5.9]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_num_list_6(self):
        # Check that str list is not accepted (string format)
        plugin = self.initial_setup()
        key = "num_list_param"
        value = "[value, second6]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_num_list_7(self):
        # Check that float and int list is accepted (string format)
        plugin = self.initial_setup()
        key = "num_list_param"
        value = "[10.4, 30.6, 5]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_num_list_8(self):
        # Check that float only list is accepted (string format)
        plugin = self.initial_setup()
        key = "num_list_param"
        value = "[10.4, 30.6, 5.9]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_num_list_9(self):
        # Check that multiple floats inside a string are not accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = "10.4, 30.6, 5.9"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_num_list_10(self):
        # Check that empty lists are not accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = "[]"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_num_list_11(self):
        # Check that empty lists are not accepted
        plugin = self.initial_setup()
        key = "num_list_param"
        value = []

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_pos_int(self):
        # Check that positive integers are accepted
        plugin = self.initial_setup()
        key = "positive_test"
        value = 2

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_pos_int_1(self):
        # Check that negative integers are not accepted
        plugin = self.initial_setup()
        key = "positive_test"
        value = -2

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_options(self):
        # Check that valid options are accepted
        plugin = self.initial_setup()
        key = "algorithm"
        value = "SIRT"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_options_1(self):
        # Check that invalid options of correct type are not accepted
        plugin = self.initial_setup()
        key = "algorithm"
        value = "SARTT"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_options_2(self):
        # Check that the invalid type int is not accepted
        plugin = self.initial_setup()
        key = "algorithm"
        value = 4

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_multi_param(self):
        # Check that multiple integers are accepted
        plugin = self.initial_setup()
        key = "positive_test"
        value = "2;4;64"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [2, 4, 64]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_1(self):
        # Check that negative integers within the list are not accepted
        plugin = self.initial_setup()
        key = "positive_test"
        value = "-2;5;4"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [-2, 5, 4]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_multi_param_2(self):
        # Check that invalid options are not accepted
        plugin = self.initial_setup()
        key = "algorithm"
        value = "SIRT;SART;SLING"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ["SIRT", "SART", "SLING"]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_multi_param_3(self):
        # Check that multiple strings are accepted
        plugin = self.initial_setup()
        key = "algorithm"
        value = "FP;BP;SIRT"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ["FP", "BP", "SIRT"]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_4(self):
        # Check that multiple strings are accepted
        plugin = self.initial_setup()
        key = "algorithm"
        value = "FP;"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ["FP"]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_5(self):
        # ;; is ignored and the two options are seperated
        plugin = self.initial_setup()
        key = "algorithm"
        value = "FP;;SART"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ["FP", "SART"]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_6(self):
        # ; is ignored and options are checked as a list
        plugin = self.initial_setup()
        key = "algorithm"
        value = ";FP"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ["FP"]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_7(self):
        # Check that syntax fails
        plugin = self.initial_setup()
        key = "algorithm"
        value = ":FP"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_multi_param_8(self):
        # Check that syntax works. If colon included in the first item
        # then this overwrites items after ;
        plugin = self.initial_setup()
        key = "int_param"
        value = "1:30:1;"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                  11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                  21, 22, 23, 24, 25, 26, 27, 28, 29]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_9(self):
        # Check that syntax fails
        plugin = self.initial_setup()
        key = "int_param"
        value = "1:3a;"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_multi_param_10(self):
        # Check that tuple list is accepted
        plugin = self.initial_setup()
        key = "vocentering_search_area"
        value = "(2,4);(5,65);(86,87);"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [(2, 4), (5, 65), (86, 87)]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_11(self):
        plugin = self.initial_setup()
        key = "ica_w_init"
        value = "[8,8,9];[78,89];[78,0,0];[9]"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [[8, 8, 9], [78, 89], [78, 0, 0], [9]]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_12(self):
        # Range should fail as length should be 2
        plugin = self.initial_setup()
        key = "range_param"
        value = "(2,7);(3,8);(0,4,6)"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [(2, 7), (3, 8), (0, 4, 6)]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_multi_param_13(self):
        # One tuple, one list, the range type check should allow a list as well
        plugin = self.initial_setup()
        key = "range_param"
        value = "(2,7);[3,8];(0,4)"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_multi_param_14(self):
        # Check that tuples are accepted
        plugin = self.initial_setup()
        key = "vocentering_search_area"
        value = "(4,5);(7,0);"

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [(4, 5), (7,0)]
        self.assertEqual(val_list, result)


        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_dict(self):
        # Check that dict is accepted
        plugin = self.initial_setup()
        key = "dict_param"
        value = {1: 2}

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_dict_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "dict_param"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_dict_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = "dict_param"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_dict_3(self):
        # Check that str dict is accepted
        plugin = self.initial_setup()
        key = "dict_param"
        value = {"example_key": "method"}

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_dict_4(self):
        # Check that dict within a dict is accepted
        plugin = self.initial_setup()
        key = "dict_param"
        value = {"example_key": {"second_dict":"method"}}

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_dict_5(self):
        # Check that dict within a dict is accepted (string format)
        plugin = self.initial_setup()
        key = "dict_param"
        value = "{'example_key': {'second_dict':'method'}}"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_dict_6(self):
        # Check that list within a dict is accepted (string format)
        plugin = self.initial_setup()
        key = "dict_param"
        value = "{'example_key': [4,5,6,7]}"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_dict_7(self):
        # Check that list within a dict is accepted
        plugin = self.initial_setup()
        key = "dict_param"
        value = {'example_key': [4,5,6,7]}

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_float_dict(self):
        # Check that dict with integer keys and float values is accepted
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = {1: 2.0}

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_float_dict_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = 8

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_float_dict_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = [2, 3, 4, 5]

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_float_dict_3(self):
        # Check that incorrect str dict is not accepted
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = {3: "true"}

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_float_dict_4(self):
        # Check that int and int(accepted as float) dict is accepted
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = {3: 5}

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_float_dict_5(self):
        # Check that incorrect str dict is not accepted
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = {3.8: 5.0}

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_float_dict_6(self):
        # Check that incorrect int dict is not accepted (string format)
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = "{3.8: 5.0}"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_float_dict_7(self):
        # Check that incorrect str dict is not accepted (string format)
        plugin = self.initial_setup()
        key = "cor_dict_param"
        # True is recognised as an integer value of 1
        value = "{3: true}"
        # MAYBE run yaml config or error message run on the input values?
        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        # Fails and returns true with {3:1}
        self.assertFalse(valid_modification)

    def test_int_float_dict_8(self):
        # Check that correct dict is accepted (string format)
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = "{3: 9.0}"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)

    def test_int_float_dict_9(self):
        # Check that incorrect str dict is not accepted (string format)
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = "{3: Another entry}"

        value_check = pu._dumps(value)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertFalse(valid_modification)

    def test_int_float_dict_10(self):
        # Check that int and int(accepted as float) dict is accepted
        plugin = self.initial_setup()
        key = "cor_dict_param"
        value = {3:5}

        value_check = pu._dumps(value)
        self.assertEqual({3:5}, value_check)
        valid_modification, error_str = param_u.is_valid(
            key, value_check, plugin.p_dict[key]
        )
        self.assertTrue(valid_modification)


if __name__ == "__main__":
    unittest.main()
