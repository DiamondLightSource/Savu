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

import os
import unittest
import numpy as np
import savu.test.test_utils as tu
from savu.plugins.basic_operations.no_process_plugin import NoProcessPlugin


class MaxFramesTest(unittest.TestCase):

    def __get_slice_list_dict(self, data, pData, pattern, nFrames, dtype,
                              processes):
        data.exp.meta_data.set('processes', processes)
        pData._plugin = NoProcessPlugin() # dummy plugin to set required params
        pData.plugin_data_setup(pattern, nFrames)
        pData._set_meta_data()
        pData.plugin_data_transfer_setup()
        sl_dict = \
            data._get_transport_data()._get_slice_lists_per_process(dtype)
        return sl_dict

    def __assert(self, pData, sl_dict, mft, mfp, nTrans, nProc, nframes=None):
        self.assertEqual(pData._get_max_frames_transfer(), mft)
        self.assertEqual(pData._get_max_frames_process(), mfp)
        self.assertEqual(len(sl_dict['transfer']), nTrans)
        self.assertEqual(len(sl_dict['process']), nProc)

        # checking the distribution of frames is good
        if nframes:
            temp = ((nframes/float(mft)) % 1)
            self.assertTrue((temp > 0.85 or temp == 0.0))

    def __get_system_parameters_file(self):
        path = os.path.join(os.path.dirname(__file__), "system_parameters.yml")
        return path

    def test1_single_threaded(self):
        loader = "full_field_loaders.random_3d_tomo_loader"
        params = {'size': (140, 1, 1)}  # data size is (136, 1, 1)
        sys_file = self.__get_system_parameters_file()
        # create a process list?

        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', 'p')
        self.__assert(pData, sl_dict, 17, 1, 8, 17, nframes=136)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', 'p')
        self.__assert(pData, sl_dict, 17, 17, 8, 1, nframes=136)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 8, 'in', 'p')
        self.__assert(pData, sl_dict, 16, 8, 9, 2)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 3, 'in', 'p')
        self.__assert(pData, sl_dict, 18, 3, 8, 6)

    def test2_single_threaded(self):
        loader = "full_field_loaders.random_3d_tomo_loader"
        params = {'size': (313, 1, 1)}  # data size is (309, 1, 1)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', 'p')
        self.__assert(pData, sl_dict, 31, 1, 10, 31, nframes=309)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', 'p')
        self.__assert(pData, sl_dict, 31, 31, 10, 1, nframes=309)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 5, 'in', 'p')
        self.__assert(pData, sl_dict, 20, 5, 16, 4)

    def test3_single_threaded(self):
        loader = "full_field_loaders.random_3d_tomo_loader"
        params = {'size': (45, 1, 1)}  # data size is (41, 1, 1)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', 'p')
        self.__assert(pData, sl_dict, 21, 1, 2, 21, nframes=41)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', 'p')
        self.__assert(pData, sl_dict, 21, 21, 2, 1, nframes=41)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 17, 'in', 'p')
        self.__assert(pData, sl_dict, 17, 17, 3, 1)

    def test4_single_threaded(self):
        loader = "full_field_loaders.random_3d_tomo_loader"
        params = {'size': (4500, 1, 1)}  # data size is (4496, 1, 1)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', 'p')
        self.__assert(pData, sl_dict, 16, 1, 281, 16, nframes=4496)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', 'p')
        self.__assert(pData, sl_dict, 16, 16, 281, 1, nframes=4496)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 6, 'in', 'p')
        self.__assert(pData, sl_dict, 18, 6, 250, 3)

    def test1_parallel(self):
        loader = "random_hdf5_loader"
        params = {}
        processes = ['p']*2        
        params['patterns'] = ['PROJECTION.0s.1s.2c.3c.4s']
        params['axis_labels'] = ['val%d.unit' % i for i in range(5)]
        params['size'] = (4, 3, 1, 1, 4)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))
        data.dtype = np.dtype(np.float32)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', processes)
        self.__assert(pData, sl_dict, 2, 1, 12, 2, nframes=4*3*4)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', processes)
        self.__assert(pData, sl_dict, 2, 2, 12, 1, 4*3*4)

    def test2_parallel(self):
        loader = "random_hdf5_loader"
        params = {}
        processes = ['p']*3        
        params['patterns'] = ['PROJECTION.0s.1s.2c.3c.4s']
        params['axis_labels'] = ['val%d.unit' % i for i in range(5)]
        params['size'] = (1, 1, 1, 1, 1)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))
        data.dtype = np.dtype(np.float32)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', processes)
        self.__assert(pData, sl_dict, 1, 1, 1, 1, 1)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', processes)
        self.__assert(pData, sl_dict, 1, 1, 1, 1, 1)

    def test3_parallel(self):
        loader = "random_hdf5_loader"
        params = {}
        processes = ['p']*4        
        params['patterns'] = ['PROJECTION.0s.1s.2c.3c.4s']
        params['axis_labels'] = ['val%d.unit' % i for i in range(5)]
        params['size'] = (15, 13, 1, 1, 4)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))
        data.dtype = np.dtype(np.float32)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', processes)
        self.__assert(pData, sl_dict, 4, 1, 52, 4, 15*13*4)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', processes)
        self.__assert(pData, sl_dict, 4, 4, 52, 1, 15*13*4)

    def test4_parallel(self):
        loader = "full_field_loaders.random_3d_tomo_loader"
        processes = ['p']*20
        params = {'size': (24, 1, 1)}  # data size is (20, 1, 1)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', processes)
        self.__assert(pData, sl_dict, 1, 1, 1, 1, 20)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', processes)
        self.__assert(pData, sl_dict, 1, 1, 1, 1, 20)

    def test5_parallel(self):
        loader = "full_field_loaders.random_3d_tomo_loader"
        processes = ['p']*15
        params = {'size': (24, 1, 1)}  # data size is (20, 1, 1)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', processes)
        self.__assert(pData, sl_dict, 2, 1, 1, 2, 20)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', processes)
        self.__assert(pData, sl_dict, 2, 2, 1, 1, 20)

    def test6_parallel(self):
        loader = "full_field_loaders.random_3d_tomo_loader"
        processes = ['p']*15
        params = {'size': (4500, 1, 1)}  # data size is (4496, 1, 1)
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', processes)
        self.__assert(pData, sl_dict, 30, 1, 10, 30, 4496)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', processes)
        self.__assert(pData, sl_dict, 30, 30, 10, 1, 4496)

    def test7_parallel(self):
        loader = "random_hdf5_loader"
        params = {}
        params['patterns'] = ['PROJECTION.0s.1s.2c.3c.4s']
        params['axis_labels'] = ['val%d.unit' % i for i in range(5)]
        params['size'] = (4, 3, 1, 1, 4)
        processes = ['p']*3
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))
        data.dtype = np.dtype(np.float32)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', processes)
        self.__assert(pData, sl_dict, 2, 1, 8, 2, 4*3*4)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', processes)
        self.__assert(pData, sl_dict, 2, 2, 8, 1, 4*3*4)

    def test8_parallel(self):
        loader = "random_hdf5_loader"
        params = {}
        params['patterns'] = ['PROJECTION.0s.1s.2c.3c.4s']
        params['axis_labels'] = ['val%d.unit' % i for i in range(5)]
        params['size'] = (450, 36, 1, 1, 14)
        processes = ['p']*36
        sys_file = self.__get_system_parameters_file()
        data, pData = tu.get_data_object(tu.load_random_data(
                loader, params, system_params=sys_file, fake=True))
        data.dtype = np.dtype(np.float32)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'single', 'in', processes)
        self.__assert(pData, sl_dict, 13, 1, 490, 13)

        sl_dict = self.__get_slice_list_dict(
                data, pData, 'PROJECTION', 'multiple', 'in', processes)
        self.__assert(pData, sl_dict, 13, 13, 490, 1)
#
if __name__ == "__main__":
    unittest.main()
