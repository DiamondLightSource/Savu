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

import savu.test.test_utils as tu


class Test(unittest.TestCase):

    def testGetExampleData(self):
        raw_data = tu.get_nexus_test_data()
        self.assertEqual(raw_data.data.data.shape, (111, 135, 160),
                         "Data is not the correct shape, was " +
                         str(raw_data.data.data.shape))
        self.assertEqual(raw_data.control.data.shape, (111,),
                         "Control is not the correct shape, was " +
                         str(raw_data.control.data.shape))
        self.assertEqual(raw_data.image_key.data.shape, (111,),
                         "Image_key is not the correct shape, was " +
                         str(raw_data.image_key.data.shape))
        self.assertEqual(raw_data.rotation_angle.data.shape, (111,),
                         "Rotation_Angle is not the correct shape, was " +
                         str(raw_data.rotation_angle.data.shape))

if __name__ == "__main__":
    unittest.main()
