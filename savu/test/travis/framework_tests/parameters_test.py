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

import unittest

from collections import OrderedDict
import savu.plugins.docstring_parser as dp


class ParametersTest(unittest.TestCase):
    def test_regular_param(self):
        """
        reg_param:
             description: Testing a regular param.
             default: 3.0
             dtype: float
             visibility: basic

        """
        parsed_dict = dp.load_yaml_doc(self.test_regular_param.__doc__)
        param = OrderedDict(
                     [("reg_param",
                            OrderedDict([
                            ("description", "Testing a regular param."),
                            ("default", 3.0),
                            ("dtype", "float"),
                            ("visibility", "basic"),
                        ]),) ])
        self.assertDictEqual(parsed_dict, param)


if __name__ == "__main__":
    unittest.main()
