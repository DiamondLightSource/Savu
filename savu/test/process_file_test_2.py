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
.. module:: framework_test
   :platform: Unix
   :synopsis: unittest test class for plugin utils

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest

from savu.test import test_utils as tu

from savu.test.process_file_test import FrameworkTest


class Process09Test(FrameworkTest):

    def setUp(self):
        self.process_filename = tu.get_test_data_path('process09.nxs')


class Process10Test(FrameworkTest):

    def setUp(self):
        self.process_filename = tu.get_test_data_path('process10.nxs')


class Process11Test(FrameworkTest):

    def setUp(self):
        self.process_filename = tu.get_test_data_path('process11.nxs')

if __name__ == "__main__":
    unittest.main()
