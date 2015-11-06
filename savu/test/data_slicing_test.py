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
from savu.data.data_structures import Padding


class Test(unittest.TestCase):

    def test_slice(self):
        data, pData = tu.get_data_object(tu.load_test_data("tomo"))

        pData.plugin_data_setup('PROJECTION', 1)
        gsl = data.get_grouped_slice_list()
        self.assertEqual(len(gsl), 91)
        self.assertEqual(len(gsl[0]), 3)

        pData.plugin_data_setup('SINOGRAM', 1)
        gsl = data.get_grouped_slice_list()
        self.assertEqual(len(gsl), 135)
        self.assertEqual(len(gsl[0]), 3)

    def test_slice_group(self):
        data, pData = tu.get_data_object(tu.load_test_data("tomo"))

        pData.plugin_data_setup('PROJECTION', 8)
        gsl = data.get_grouped_slice_list()
        self.assertEqual(len(gsl), 12)
        self.assertEqual(len(gsl[0]), 3)

        pData.plugin_data_setup('SINOGRAM', 8)
        gsl = data.get_grouped_slice_list()
        self.assertEqual(len(gsl), 17)
        self.assertEqual(len(gsl[0]), 3)

    def test_get_slice_list_per_process(self):
        exp = tu.load_test_data("tomo")
        data, pData = tu.get_data_object(exp)

        processes = ['t', 't', 't', 't']

        pData.plugin_data_setup('PROJECTION', 1)
        sl = data.single_slice_list()
        total = []
        for i in range(len(processes)):
            tu.set_process(exp, i, processes)
            total.append(data.get_slice_list_per_process(exp.meta_data))
        self.assertEqual(len(sl), sum(len(t) for t in total))

        pData.plugin_data_setup('SINOGRAM', 1)
        sl = data.single_slice_list()
        total = []
        for i in range(len(processes)):
            tu.set_process(exp, i, processes)
            total.append(data.get_slice_list_per_process(exp.meta_data))
        self.assertEqual(len(sl), sum(len(t) for t in total))

        pData.plugin_data_setup('PROJECTION', 8)
        sl = data.get_grouped_slice_list()
        total = []
        for i in range(len(processes)):
            tu.set_process(exp, i, processes)
            total.append(data.get_slice_list_per_process(exp.meta_data))
        self.assertEqual(len(sl), sum(len(t) for t in total))

        pData.plugin_data_setup('SINOGRAM', 1)
        sl = data.get_grouped_slice_list()
        total = []
        for i in range(len(processes)):
            tu.set_process(exp, i, processes)
            total.append(data.get_slice_list_per_process(exp.meta_data))
        self.assertEqual(len(sl), sum(len(t) for t in total))

    def test_get_padded_slice_data(self):
        data, pData = tu.get_data_object(tu.load_test_data("tomo"))

        data.finalise_patterns()
        pData.plugin_data_setup('PROJECTION', 1)
        data.padding = {'pad_multi_frames': 10}
        padding = Padding(pData.get_pattern())
        padding.get_padding_directions()
        for key in data.padding.keys():
            getattr(padding, key)(data.padding[key])
        return padding.get_padding_directions()

#        in_data.padding = {'pad_multi_frames':10, 'pad_edges':5}
#                
#        in_data.padding = {'pad_direction':[0, 3]}
#        
#        in_data.padding = {'pad_direction':[1, 3]}
#
#        in_data.padding = {'pad_direction':[2, 3]}
#
#        in_data.padding = {'pad_direction':[0, 3], 'pad_direction':[1, 4]}
#        
#        in_data.padding = {'pad_direction':[0, 3], 'pad_direction':[1, 4],
#                           'pad_direction':[2, 5]}
        

        
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
