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

from __future__ import print_function, division, absolute_import

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

if __name__ == "__main__":
    unittest.main()
