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
  
# test single_slice_list
      
    def test_slice(self):
        data = tu.load_test_data("tomo")
        data.set_nFrames(1)
        data.set_current_pattern_name("PROJECTION")
        gsl = data.get_grouped_slice_list()
        self.assertEqual(len(gsl), 91)
        self.assertEqual(len(gsl[0]), 3)

        data.set_current_pattern_name("SINOGRAM")
        gsl = data.get_grouped_slice_list()
        self.assertEqual(len(gsl), 135)
        self.assertEqual(len(gsl[0]), 3)
        
        
    def test_slice_group(self):
        data = tu.load_test_data("tomo")
        data.set_nFrames(8)
        data.set_current_pattern_name("PROJECTION")
        gsl = data.get_grouped_slice_list()
        self.assertEqual(len(gsl), 12)
        self.assertEqual(len(gsl[0]), 3)

#        sl = du.get_slice_list(data, struct.CD_SINOGRAM)
#        gsl = du.group_slice_list(sl, 8)
#        self.assertEqual(len(gsl), 17)
#        self.assertEqual(len(gsl[0]), 3)
#        
#        sl = du.get_slice_list(data, struct.CD_ROTATION_AXIS)
#        gsl = du.group_slice_list(sl, 8)
#        self.assertEqual(len(gsl), 2700)
#        for group in gsl:
#            self.assertEqual(len(group), 3)
    
#    def test_get_slice_list_per_process(self):
#        data = tu.get_nx_tomo_test_data()
#        sl = du.get_grouped_slice_list(data, struct.CD_PROJECTION, 8)
#        sl0 = du.get_slice_list_per_process(sl, 0, 4)
#        sl1 = du.get_slice_list_per_process(sl, 1, 4)
#        sl2 = du.get_slice_list_per_process(sl, 2, 4)
#        sl3 = du.get_slice_list_per_process(sl, 3, 4)
#        slt = sl0 + sl1 + sl2 + sl3
#        self.assertListEqual(sl, slt)
#        
#        sl = du.get_grouped_slice_list(data, struct.CD_SINOGRAM, 8)
#        sl0 = du.get_slice_list_per_process(sl, 0, 4)
#        sl1 = du.get_slice_list_per_process(sl, 1, 4)
#        sl2 = du.get_slice_list_per_process(sl, 2, 4)
#        sl3 = du.get_slice_list_per_process(sl, 3, 4)
#        slt = sl0 + sl1 + sl2 + sl3
#        self.assertListEqual(sl, slt)
#        
#        sl = du.get_grouped_slice_list(data, struct.CD_ROTATION_AXIS, 8)
#        sl0 = du.get_slice_list_per_process(sl, 0, 4)
#        sl1 = du.get_slice_list_per_process(sl, 1, 4)
#        sl2 = du.get_slice_list_per_process(sl, 2, 4)
#        sl3 = du.get_slice_list_per_process(sl, 3, 4)
#        slt = sl0 + sl1 + sl2 + sl3
#        self.assertListEqual(sl, slt)

#    def test_get_padded_slice_data(self):
#        # run the loader for 24737.nxs
#        data = tu.load_test_data()
#        data = tu.get_nx_tomo_test_data()
#        sl = data.get_grouped_slice_list(data, struct.CD_PROJECTION, 8)
#        
#        padding_dict = {}
#        padding_dict[struct.CD_ROTATION_AXIS] = 1
#
#        psl0ra = du.get_padded_slice_data(sl[0], padding_dict, data)
#        psl5ra = du.get_padded_slice_data(sl[5], padding_dict, data)
#        self.assertEqual(psl0ra.shape, (10, 135, 160))
#        self.assertEqual(psl5ra.shape, (10, 135, 160))

#    def test_get_padded_slice_data_2(self):
#        data = tu.get_nx_tomo_test_data()
#        sl = du.get_grouped_slice_list(data, struct.CD_ROTATION_AXIS, 8)
#        
#        padding_dict = {}
#        padding_dict[struct.CD_ROTATION_AXIS] = 1
#        
#        psl0_0 = du.get_padded_slice_data(sl[0], padding_dict, data)
#        psl5_0 = du.get_padded_slice_data(sl[5], padding_dict, data)
#        self.assertEqual(psl0_0.shape, (113, 8))
#        self.assertEqual(psl5_0.shape, (113, 8))
#
#
#    def test_get_padded_slice_data_3(self):
#        data = tu.get_nx_tomo_test_data()
#        sl = du.get_grouped_slice_list(data, struct.CD_ROTATION_AXIS, 8)
#        
#        padding_dict = {}
#        padding_dict[struct.CD_PROJECTION] = 1
#        
#        psl0_0 = du.get_padded_slice_data(sl[0], padding_dict, data)
#        psl5_0 = du.get_padded_slice_data(sl[5], padding_dict, data)
#        self.assertEqual(psl0_0.shape, (111, 3, 10))
#        self.assertEqual(psl5_0.shape, (111, 3, 10))
#
#
#    def test_get_unpadded_slice_data(self):
#        data = tu.get_nx_tomo_test_data()
#        sl = du.get_grouped_slice_list(data, struct.CD_ROTATION_AXIS, 8)
#        
#        padding_dict = {}
#        padding_dict[struct.CD_PROJECTION] = 1
#        
#        psl0_0 = du.get_padded_slice_data(sl[0], padding_dict, data)
#        psl5_0 = du.get_padded_slice_data(sl[5], padding_dict, data)
#        self.assertEqual(psl0_0.shape, (111, 3, 10))
#        self.assertEqual(psl5_0.shape, (111, 3, 10))
#        
#        raw0 = data.data[sl[0]]
#        psl0_un = du.get_unpadded_slice_data(sl[0], padding_dict, data, psl0_0)
#        self.assertEqual(psl0_un.squeeze().shape, raw0.shape)
#        self.assertEqual(psl0_un.sum(), raw0.sum())
#        
#        raw5 = data.data[sl[5]]
#        psl5_un = du.get_unpadded_slice_data(sl[5], padding_dict, data, psl5_0)
#        self.assertEqual(psl5_un.squeeze().shape, raw5.shape)
#        self.assertEqual(psl5_un.sum(), raw5.sum())
#
#    def test_get_unpadded_slice_data_2(self):
#        data = tu.get_nx_tomo_test_data()
#        sl = du.get_grouped_slice_list(data, struct.CD_SINOGRAM, 1)
#        
#        padding_dict = {}
#        #padding_dict[struct.CD_PROJECTION] = 1
#        
#        psl0_0 = du.get_padded_slice_data(sl[0], padding_dict, data)
#        psl5_0 = du.get_padded_slice_data(sl[5], padding_dict, data)
#        self.assertEqual(psl0_0.shape, (111, 1, 160))
#        self.assertEqual(psl5_0.shape, (111, 1, 160))
#        
#        raw0 = data.data[sl[0]]
#        psl0_un = du.get_unpadded_slice_data(sl[0], padding_dict, data, psl0_0)
#        self.assertEqual(psl0_un.shape, raw0.shape) # here
#        self.assertEqual(psl0_un.sum(), raw0.sum())
#        
#        raw5 = data.data[sl[5]]
#        psl5_un = du.get_unpadded_slice_data(sl[5], padding_dict, data, psl5_0)
#        self.assertEqual(psl5_un.shape, raw5.shape)
#        self.assertEqual(psl5_un.sum(), raw5.sum())


if __name__ == "__main__":
    unittest.main()
