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

class ParameterTypeTest(unittest.TestCase):

    def initial_setup(self):
        ppath = 'savu.plugins.basic_operations.no_process'
        plugin = pu.load_class(ppath)()
        plugin._populate_default_parameters()
        return plugin

    def test_int(self):
        # Check that integer is accepted
        plugin = self.initial_setup()
        key = 'other'
        valid_modification = plugin.tools.modify(plugin.parameters, 7, key)
        self.assertTrue(valid_modification)

    def test_int_1(self):
        # Check that string is declined
        plugin = self.initial_setup()
        key = 'other'
        valid_modification = plugin.tools.modify(plugin.parameters, 'hello', key)
        self.assertFalse(valid_modification)

    def test_int_2(self):
        # Should float be changed to an integer?
        plugin = self.initial_setup()
        key = 'other'
        valid_modification = plugin.tools.modify(plugin.parameters, 7.0, key)
        self.assertFalse(valid_modification)

    def test_yaml(self):
        # Check that yaml file is accepted
        plugin = self.initial_setup()
        key = 'yaml_file'
        value = 'savu/plugins/loaders/full_field_loaders/nxtomo_loader.yaml'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_yaml_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'yaml_file'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_yaml_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = 'yaml_file'
        value = [2, 3, 4, 5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_string(self):
        # Check that string is accepted
        plugin = self.initial_setup()
        key = 'pattern'
        value = 'An example'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_string_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'pattern'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_string_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = 'pattern'
        value = [2,3,4,5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_tuple(self):
        # Check that tuple is accepted
        plugin = self.initial_setup()
        key = 'vocentering_search_area'
        value = (1, 2)
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_tuple_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'vocentering_search_area'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_tuple_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = 'vocentering_search_area'
        value = [2, 3, 4, 5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_list(self):
        # Check that list is accepted
        plugin = self.initial_setup()
        key = 'ica_w_init'
        value = [2,3,4,5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'ica_w_init'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = 'ica_w_init'
        value = 'Testing str'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_int_list(self):
        # Check that int list is accepted
        plugin = self.initial_setup()
        key = 'integer_list_param'
        value = [2,3,4,5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_int_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'integer_list_param'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_int_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = 'integer_list_param'
        value = 'Testing str'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_int_list_3(self):
        # Check that str list is not accepted
        plugin = self.initial_setup()
        key = 'integer_list_param'
        value = ['value','second6']
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_string_list(self):
        # Check that string list is accepted
        plugin = self.initial_setup()
        key = 'string_list_param'
        value = ['value','second6']
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_string_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'string_list_param'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_string_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = 'string_list_param'
        value = 'Testing str'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_string_list_3(self):
        # Check that int list is not accepted
        plugin = self.initial_setup()
        key = 'string_list_param'
        value = [2,3,4,5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_num_list(self):
        # Check that int list is accepted
        plugin = self.initial_setup()
        key = 'num_list_param'
        value = [2,3,4,5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_num_list_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'num_list_param'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_num_list_2(self):
        # Check that str is not accepted
        plugin = self.initial_setup()
        key = 'num_list_param'
        value = 'Testing str'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_num_list_3(self):
        # Check that str list is not accepted
        plugin = self.initial_setup()
        key = 'num_list_param'
        value = ['value','second6']
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_num_list_4(self):
        # Check that float and int list is accepted
        plugin = self.initial_setup()
        key = 'num_list_param'
        value = [10.4,30.6,5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_num_list_5(self):
        # Check that float only list is accepted
        plugin = self.initial_setup()
        key = 'num_list_param'
        value = [10.4,30.6,5.9]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_pos_int(self):
        # Check that positive integers are accepted
        plugin = self.initial_setup()
        key = 'positive_test'
        value = 2
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_pos_int_1(self):
        # Check that negative integers are not accepted
        plugin = self.initial_setup()
        key = 'positive_test'
        value = -2
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_options(self):
        # Check that valid options are accepted
        plugin = self.initial_setup()
        key = 'algorithm'
        value = 'SIRT'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_options_1(self):
        # Check that invalid options of correct type are not accepted
        plugin = self.initial_setup()
        key = 'algorithm'
        value = 'SARTT'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_options_2(self):
        # Check that the invalid type int is not accepted
        plugin = self.initial_setup()
        key = 'algorithm'
        value = 4
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_multi_param(self):
        # Check that multiple integers are accepted
        plugin = self.initial_setup()
        key = 'positive_test'
        value = '2;4;64'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [2,4,64]
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)


    def test_multi_param_1(self):
        # Check that negative integers within the list are not accepted
        plugin = self.initial_setup()
        key = 'positive_test'
        value = '-2;5;4'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [-2, 5, 4]
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)


    def test_multi_param_2(self):
        # Check that invalid options are not accepted
        plugin = self.initial_setup()
        key = 'algorithm'
        value = 'SIRT;SART;SLING'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ['SIRT','SART','SLING']
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_multi_param_3(self):
        # Check that multiple strings are accepted
        plugin = self.initial_setup()
        key = 'algorithm'
        value = 'FP;BP;SIRT'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ['FP','BP','SIRT']
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)


    def test_multi_param_4(self):
        # Check that multiple strings are accepted
        plugin = self.initial_setup()
        key = 'algorithm'
        value = 'FP;'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ['FP']
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)


    def test_multi_param_5(self):
        # ;; is ignored and the two options are seperated
        plugin = self.initial_setup()
        key = 'algorithm'
        value = 'FP;;SART'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ['FP', 'SART']
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)


    def test_multi_param_6(self):
        # ; is ignored and options are checked as a list
        plugin = self.initial_setup()
        key = 'algorithm'
        value = ';FP'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = ['FP']
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)


    def test_multi_param_7(self):
        # Check that syntax fails
        plugin = self.initial_setup()
        key = 'algorithm'
        value = ':FP'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_multi_param_8(self):
        # Check that syntax works. If colon included in the first item
        # then this overwrites items after ;
        plugin = self.initial_setup()
        key = 'other'
        value = '1:30:1;'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                  23, 24, 25, 26, 27, 28, 29]
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)


    def test_multi_param_9(self):
        # Check that syntax fails
        plugin = self.initial_setup()
        key = 'other'
        value = '1:3a;'
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_multi_param_10(self):
        # Check that tuple list is accepted
        plugin = self.initial_setup()
        key = 'vocentering_search_area'
        value = '(2,4);(5,65);(86,87);'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [(2,4),(5,65),(86,87)]
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_multi_param_11(self):
        plugin = self.initial_setup()
        key = 'ica_w_init'
        value = '[8,8,9];[78,89];[78,0,0];[9]'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [[8,8,9],[78,89],[78,0,0],[9]]
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_multi_param_12(self):
        # Range should fail as length should be 2
        plugin = self.initial_setup()
        key = 'range_param'
        value = '(2,7);(3,8);(0,4,6)'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [(2,7),(3,8),(0,4,6)]
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_multi_param_13(self):
        # One tuple, one list, should fail
        plugin = self.initial_setup()
        key = 'range_param'
        value = '(2,7);[3,8];(0,4)'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)


    def test_multi_param_14(self):
        # Check that one value inside a tuple list is accepted
        plugin = self.initial_setup()
        key = 'vocentering_search_area'
        value = '(4,5);(7);'

        # Check the multi parameter value is changed to a list correctly
        val_list, error_str = pu.convert_multi_params(key, value)
        result = [(4,5),(7,)]
        self.assertEqual(val_list, result)

        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)


    def test_dict(self):
        # Check that dict is accepted
        plugin = self.initial_setup()
        key = 'dict_param'
        value = {1:2}
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_dict_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'dict_param'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_dict_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = 'dict_param'
        value = [2, 3, 4, 5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_dict_3(self):
        # Check that str dict is accepted
        plugin = self.initial_setup()
        key = 'dict_param'
        value = {'example_key':'method'}
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_int_float_dict(self):
        # Check that dict with integer keys and float values is accepted
        plugin = self.initial_setup()
        key = 'cor_dict_param'
        value = {1:2.0}
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_int_float_dict_1(self):
        # Check that integer is not accepted
        plugin = self.initial_setup()
        key = 'cor_dict_param'
        value = 8
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_int_float_dict_2(self):
        # Check that list is not accepted
        plugin = self.initial_setup()
        key = 'cor_dict_param'
        value = [2, 3, 4, 5]
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_int_float_dict_3(self):
        # Check that incorrect str dict is not accepted
        plugin = self.initial_setup()
        key = 'cor_dict_param'
        value = {3:'true'}
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)

    def test_int_float_dict_4(self):
        # Check that int and int(accepted as float) dict is accepted
        plugin = self.initial_setup()
        key = 'cor_dict_param'
        value = {3:5}
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertTrue(valid_modification)

    def test_int_float_dict_5(self):
        # Check that incorrect str dict is not accepted
        plugin = self.initial_setup()
        key = 'cor_dict_param'
        value = {3.8:5.0}
        valid_modification = plugin.tools.modify(plugin.parameters, value, key)
        self.assertFalse(valid_modification)


if __name__ == "__main__":
    unittest.main()
