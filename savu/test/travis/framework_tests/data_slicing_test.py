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
from savu.data.data_structures.data_add_ons import Padding
from savu.data.transport_data.hdf5_transport_data import \
    TransferData, ProcessData


class Test(unittest.TestCase):

    def _get_grouped_transfer_slice_list(self, data):
        tdata = TransferData('in', data)
        return tdata._get_slice_list(data.get_shape())

    def _get_grouped_process_slice_list(self, data):
        tdata = ProcessData('in', data)
        return tdata._get_slice_list()

    def _get_transfer_slice_list_per_process(self, data):
        
        
    def _get_process_slice_list_per_process(self, data):
        

    def test_slice(self):
        # transfer or process slice list
        data, pData = tu.get_data_object(tu.load_test_data("tomo"))

        pData.plugin_data_setup('PROJECTION', 'single')
        trans_gsl = self._get_grouped_transfer_slice_list(data)
        proc_gsl = self._get_grouped_process_slice_list(data)

        self.assertEqual(len(trans_gsl), 3)
        self.assertEqual(len(proc_gsl), 32)
        self.assertEqual(len(proc_gsl[0]), 3)

        pData.plugin_data_setup('SINOGRAM', 'single')
        trans_gsl = self._get_grouped_transfer_slice_list(data)
        proc_gsl = self._get_grouped_process_slice_list(data)

        self.assertEqual(len(trans_gsl), 5)
        self.assertEqual(len(proc_gsl), 32)
        self.assertEqual(len(proc_gsl[0]), 3)

    def test_slice_group(self):
        data, pData = tu.get_data_object(tu.load_test_data("tomo"))

        pData.plugin_data_setup('PROJECTION', 'multiple')
        trans_gsl = self._get_grouped_transfer_slice_list(data)
        proc_gsl = self._get_grouped_process_slice_list(data)

        self.assertEqual(len(trans_gsl), 3)
        self.assertEqual(len(proc_gsl), 1)
        self.assertEqual(len(proc_gsl[0]), 3)

        pData.plugin_data_setup('SINOGRAM', 'multiple')
        trans_gsl = self._get_grouped_transfer_slice_list(data)
        proc_gsl = self._get_grouped_process_slice_list(data)

        self.assertEqual(len(trans_gsl), 5)
        self.assertEqual(len(proc_gsl), 1)
        self.assertEqual(len(proc_gsl[0]), 3)

    def test_get_slice_list_per_process(self):
        exp = tu.load_test_data("tomo")
        data, pData = tu.get_data_object(exp)

        processes = ['t', 't', 't', 't']

        pData.plugin_data_setup('PROJECTION', 'single')
        sl = data._single_slice_list()
        total = []
        for i in range(len(processes)):
            tu.set_process(exp, i, processes)
            data._get_slice_list_per_process(exp.meta_data)
            total.append(data._get_slice_list_per_process(exp.meta_data)[0])
        self.assertEqual(len(sl), sum(len(t) for t in total))

        pData.plugin_data_setup('SINOGRAM', 1)
        sl = data._single_slice_list()
        total = []
        for i in range(len(processes)):
            tu.set_process(exp, i, processes)
            total.append(data._get_slice_list_per_process(exp.meta_data)[0])
        self.assertEqual(len(sl), sum(len(t) for t in total))

        pData.plugin_data_setup('PROJECTION', 8)
        sl = data._get_grouped_slice_list()
        total = []
        for i in range(len(processes)):
            tu.set_process(exp, i, processes)
            total.append(data._get_slice_list_per_process(exp.meta_data)[0])
        self.assertEqual(len(sl), sum(len(t) for t in total))

        pData.plugin_data_setup('SINOGRAM', 1)
        sl = data._get_grouped_slice_list()
        total = []
        for i in range(len(processes)):
            tu.set_process(exp, i, processes)
            total.append(data._get_slice_list_per_process(exp.meta_data)[0])
        self.assertEqual(len(sl), sum(len(t) for t in total))

    def test_get_padded_slice_data(self):
        data, pData = tu.get_data_object(tu.load_test_data("tomo"))

        data._finalise_patterns()
        pData.plugin_data_setup('PROJECTION', 1)
        data.padding = {'pad_multi_frames': 10}
        padding = Padding(pData.get_pattern())
        for key in data.padding.keys():
            getattr(padding, key)(data.padding[key])
        return padding._get_padding_directions()

if __name__ == "__main__":
    unittest.main()
