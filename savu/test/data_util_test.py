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

import savu.data.structures as struct
import savu.data.utils as du
import savu.test.test_utils as tu

class Test(unittest.TestCase):

    def test_slice_list(self):
        data = tu.get_nx_tomo_test_data()
        sl = du.get_slice_list(data, struct.CD_PROJECTION)
        self.assertEqual(len(sl), 111)
        sl = du.get_slice_list(data, struct.CD_SINOGRAM)
        self.assertEqual(len(sl), 135)
        sl = du.get_slice_list(data, struct.CD_ROTATION_AXIS)
        self.assertEqual(len(sl), 21600)
        
    def test_slice_group(self):
        data = tu.get_nx_tomo_test_data()
        sl = du.get_slice_list(data, struct.CD_PROJECTION)
        gsl = du.group_slice_list(sl, 8)
        self.assertEqual(len(gsl), 14)
        self.assertEqual(len(gsl[0]), 3)
        
        sl = du.get_slice_list(data, struct.CD_SINOGRAM)
        gsl = du.group_slice_list(sl, 8)
        self.assertEqual(len(gsl), 17)
        self.assertEqual(len(gsl[0]), 3)
        
        sl = du.get_slice_list(data, struct.CD_ROTATION_AXIS)
        gsl = du.group_slice_list(sl, 8)
        self.assertEqual(len(gsl), 2700)
        for group in gsl:
            self.assertEqual(len(group), 3)
    
    def test_get_slice_list_per_process(self):
        data = tu.get_nx_tomo_test_data()
        sl = du.get_grouped_slice_list(data, struct.CD_PROJECTION, 8)
        sl0 = du.get_slice_list_per_process(sl, 0, 4)
        sl1 = du.get_slice_list_per_process(sl, 1, 4)
        sl2 = du.get_slice_list_per_process(sl, 2, 4)
        sl3 = du.get_slice_list_per_process(sl, 3, 4)
        slt = sl0 + sl1 + sl2 + sl3
        self.assertListEqual(sl, slt)
        
        sl = du.get_grouped_slice_list(data, struct.CD_SINOGRAM, 8)
        sl0 = du.get_slice_list_per_process(sl, 0, 4)
        sl1 = du.get_slice_list_per_process(sl, 1, 4)
        sl2 = du.get_slice_list_per_process(sl, 2, 4)
        sl3 = du.get_slice_list_per_process(sl, 3, 4)
        slt = sl0 + sl1 + sl2 + sl3
        self.assertListEqual(sl, slt)
        
        sl = du.get_grouped_slice_list(data, struct.CD_ROTATION_AXIS, 8)
        sl0 = du.get_slice_list_per_process(sl, 0, 4)
        sl1 = du.get_slice_list_per_process(sl, 1, 4)
        sl2 = du.get_slice_list_per_process(sl, 2, 4)
        sl3 = du.get_slice_list_per_process(sl, 3, 4)
        slt = sl0 + sl1 + sl2 + sl3
        self.assertListEqual(sl, slt)

if __name__ == "__main__":
    unittest.main()
