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
.. module:: parameters_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import sys
import unittest
import numpy as np

import savu.plugins.docstring_parser as dp


class ParametersTest(unittest.TestCase):

    def _get_synopsis(self):
        mod_doc = sys.modules[self.__module__].__doc__
        mod_doc = dp._get_doc_lines(mod_doc)
        return dp._parse_args(mod_doc, '')['synopsis']

    def _set_dict(self, values):
        ddict = {}
        ddict['not_param'] = values[0]
        ddict['hide_param'] = values[1]
        ddict['user_param'] = values[2]
        ddict['param'] = values[3]
        ddict['warn'] = values[4]
        ddict['synopsis'] = values[5]
        ddict['info'] = values[6]
        return ddict

    def _get_parsed_doc(self, function):
        mod_doc_lines = dp._get_doc_lines(sys.modules[self.__module__].__doc__)
        lines = dp._get_doc_lines(function.__doc__)
        return dp._parse_args(mod_doc_lines, lines)

    def test_regular_param(self):
        """
        :param reg_param: Testing a regular param. Default: 3.0.
        """
        parsed_dict = self._get_parsed_doc(self.test_regular_param)
        param = [{'default': 3.0, 'dtype': float, 'name': 'reg_param',
                  'desc': 'Testing a regular param.'}]
        manual_dict = self._set_dict([[], [], [], param, '',
                                     self._get_synopsis(), ''])
        self.assertDictEqual(parsed_dict, manual_dict)

    def test_hidden_param(self):
        """
        :*param hidden_param: Testing a hidden param. Default: None.
        """
        parsed_dict = self._get_parsed_doc(self.test_hidden_param)
        param = [{'default': None, 'dtype': type(None), 'name': 'hidden_param',
                  'desc': 'Testing a hidden param.'}]
        manual_dict = self._set_dict([[], ['hidden_param'], [], param, '',
                                     self._get_synopsis(), ''])
        self.assertDictEqual(parsed_dict, manual_dict)

    def test_user_param(self):
        """
        :u*param user_param: Testing a user param. Default: 10.
        """
        parsed_dict = self._get_parsed_doc(self.test_user_param)
        param = [{'default': 10, 'dtype': int, 'name': 'user_param',
                  'desc': 'Testing a user param.'}]
        manual_dict = self._set_dict([[], [], ['user_param'], param, '',
                                     self._get_synopsis(), ''])
        self.assertDictEqual(parsed_dict, manual_dict)

    def test_fixed_param(self):
        """
        :*param fixed_param: Testing a fixed param. Default: ['s1', 's2'].
        """
        parsed_dict = self._get_parsed_doc(self.test_fixed_param)
        param = [{'default': ['s1', 's2'], 'dtype': list,
                  'name': 'fixed_param', 'desc': 'Testing a fixed param.'}]
        manual_dict = self._set_dict([[], ['fixed_param'], [], param, '',
                                     self._get_synopsis(), ''])
        self.assertDictEqual(parsed_dict, manual_dict)

    def test_removed_param(self):
        """
        :~param removed_param: Testing a removed param. Default: {}.
        """
        parsed_dict = self._get_parsed_doc(self.test_removed_param)
        manual_dict = self._set_dict([['removed_param'], [], [], [], '',
                                     self._get_synopsis(), ''])
        self.assertDictEqual(parsed_dict, manual_dict)


if __name__ == "__main__":
    unittest.main()
