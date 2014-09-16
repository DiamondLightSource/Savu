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
.. module:: test_util_test
   :platform: Unix
   :synopsis: unittest test class for test_utils

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest

import test_utils as tu


class Test(unittest.TestCase):

    def testGetExampleData(self):
        raw_data = tu.get_test_raw_data()
        self.assertEqual(raw_data.data.shape, (111, 135, 160),
                         "Data is not the correct shape, was " +
                         str(raw_data.data.shape))

if __name__ == "__main__":
    unittest.main()
