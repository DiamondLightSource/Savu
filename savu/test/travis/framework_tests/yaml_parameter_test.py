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
.. module:: yaml_parameter_test
   :platform: Unix
   :synopsis: unittest for plugin parameter yaml format
.. moduleauthor:: Jessica Verschoyle <jessica.verschoyle@diamond.ac.uk>

"""

import sys
import unittest
from io import StringIO

from savu.plugins.plugin_tools import PluginTools, PluginParameters

class YamlParameterTest(unittest.TestCase):

    def initial_setup(self, test_function):
        """
        Create a testing parameter class and set plugin parameters based
        upon the docstring of the passed in function - define_parameters

        :param test_function: The function containing the docstring
         text for the test
        :return: dictionary of parameters
        """
        parameter_class = PluginParameters()
        PluginToolTestingClass.define_parameters.__doc__ \
            = test_function.__doc__
        parameter_class._set_parameter_definitions(PluginToolTestingClass)
        pdefs = parameter_class.param.get_dictionary()
        return pdefs

    def test_parameter_visibility(self):
        """
        # Incorrect visibility level for regular parameter
        parameter:
            visibility: intermed
            dtype: int
            description: None
            default: 8
        """
        with self.assertRaises(Exception):
            pdefs = self.initial_setup(self.test_parameter_visibility)

    def test_parameter_visibility_missing(self):
        """
        # Missing visibility level for regular parameter
        parameter:
            dtype: int
            description: None
            default: 8
        """
        with self.assertRaises(Exception):
            pdefs = self.initial_setup(self.test_parameter_visibility_missing)

    def test_in_dataset_visibility(self):
        """
        # Incorrect visibility level for in datasets parameter
        in_datasets:
            visibility: intermediate
            dtype: int
            description: None
            default: 8
        """
        pdefs = self.initial_setup(self.test_in_dataset_visibility)

        # basic/int/adv dataset visibility levels are reset to 'datasets'
        self.assertEqual(pdefs['in_datasets']['visibility'], 'datasets')

    def test_out_dataset_visibility(self):
        """
        # Incorrect visibility level for out datasets parameter
        out_datasets:
            visibility: intermediate
            dtype: int
            description: None
            default: 8
        """
        pdefs = self.initial_setup(self.test_out_dataset_visibility)

        # basic/int/adv dataset visibility levels are reset to 'datasets'
        self.assertEqual(pdefs['out_datasets']['visibility'], 'datasets')

    def test_dataset_visibility(self):
        """
        # Incorrect visibility level for datasets parameter and mis-spelling
        in_datasets:
            visibility: basi
            dtype: int
            description: None
            default: 8
        """
        pdefs = self.initial_setup(self.test_dataset_visibility)

        # unknown dataset visibility levels are reset to 'datasets'
        self.assertEqual(pdefs['in_datasets']['visibility'], 'datasets')

    def test_dataset_hidden_visibility(self):
        """
        # Allow hidden visibility level for datasets parameter
        in_datasets:
            visibility: hidden
            dtype: [list[],list[str]]
            description: None
            default: []
        """
        pdefs = self.initial_setup(self.test_dataset_hidden_visibility)

        # hidden and not dataset visibility levels are NOT reset to 'datasets'
        self.assertEqual(pdefs['in_datasets']['visibility'], 'hidden')

    def test_parameter_dtype(self):
        """
        # Incorrect data type for regular parameter
        parameter:
            visibility: intermediate
            dtype: in
            description: None
            default: 8
        """
        with self.assertRaises(Exception):
            pdefs = self.initial_setup(self.test_parameter_dtype)

    def  test_parameter_description(self):
        """
        # Empty description for regular parameter
        parameter:
            visibility: intermediate
            dtype: [str, int]
            description:
            default: 8
        """
        # Currently no problem with empty description
        pdefs = self.initial_setup(self.test_parameter_description)

    def  test_parameter_hidden_1(self):
        """
        # Hidden parameter doesn't require options, only default value
        parameter:
            visibility: hidden
            default: 8
        """
        # Currently no problem with
        pdefs = self.initial_setup(self.test_parameter_hidden_1)

    def  test_parameter_hidden_additional_options(self):
        """
        # No error raised with unrequired parameter options
        parameter:
            visibility: hidden
            default: 8
            options: [two,three]
        """
        # Currently no problem
        pdefs = self.initial_setup(self.test_parameter_hidden_additional_options)

    def test_parameter_missing(self):
        """
        # Missing required parameter key default
        parameter:
            visibility: intermed
            dtype: int
            description:
        """
        printOutput = StringIO()  # Create StringIO object
        sys.stdout = printOutput

        with self.assertRaises(Exception):
            pdefs = self.initial_setup(self.test_parameter_missing)

        output_str = str(printOutput.getvalue())
        self.assertTrue("has missing required keys"
                        in output_str)

    def test_parameter_blank(self):
        """
        # All keys missing values
        parameter:
            visibility:
            dtype:
            description:
            default:

        """
        # Error message
        with self.assertRaises(Exception):
            pdefs = self.initial_setup(self.test_parameter_blank)

    def test_parameter_mispelt(self):
        """
        # Incorrect key spelling for visibility level key
        parameter:
            visiblity: intermediate
            dtype: int
            description:
            default: 8

        """
        printOutput = StringIO()  # Create StringIO object
        sys.stdout = printOutput

        with self.assertRaises(Exception):
            pdefs = self.initial_setup(self.test_parameter_mispelt)
        output_str = str(printOutput.getvalue())
        self.assertTrue("has unknown keys"
                        in output_str)

    def test_parameter_indent(self):
        """
        # Incorrect indentation
        parameter:
             visibility: intermediate
             dtype: int
              description: A parameter
             default: 8
        """
        printOutput = StringIO()  # Create StringIO object
        sys.stdout = printOutput

        pdefs = self.initial_setup(self.test_parameter_indent)

        self.assertTrue('Error reading the yaml structure'
                        in str(printOutput.getvalue()))


    def test_parameter_options(self):
        """
        # Options
        parameter:
            visibility: basic
            dtype: str
            description: An option list
            default: FBP
            options: [FBP, SIRT, SART]

        """
        # No error message
        pdefs = self.initial_setup(self.test_parameter_options)


    def test_parameter_options_1(self):
        """
        # Options as tuple
        parameter:
            visibility: basic
            dtype: str
            description: An option list
            default: FBP
            options: (FBP, SIRT, SART)

        """
        # No error message at the moment, but to be read in correctly
        # options must be surrounded by square brackets
        pdefs = self.initial_setup(self.test_parameter_options_1)

    def test_parameter_options_2(self):
        """
        # Invalid option choice in description
        parameter:
            visibility: basic
            dtype: str
            description:
              summary: An option list
              options:
                SIRT: One description
                SLING: Invalid option choice
                FBP: A description
            default: FBP
            options: [FBP, SIRT, SART]

        """
        # Error message
        with self.assertRaises(Exception):
            pdefs = self.initial_setup(self.test_parameter_options_2)


class PluginToolTestingClass(PluginTools):
    """A testing class"""
    def define_parameters(self):
        pass

if __name__ == "__main__":
    unittest.main()
