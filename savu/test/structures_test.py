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
.. module:: plugins_util_test
   :platform: Unix
   :synopsis: unittest test class for plugin utils

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest
import tempfile
import h5py

import numpy as np

from savu.data.structures import SliceAvailableWrapper
from savu.data.structures import SliceAlwaysAvailableWrapper
from savu.test import test_utils as tu

base_class_name = "savu.plugins.plugin"


class WrapperTest(unittest.TestCase):

    def setUp(self):
        tf = tempfile.NamedTemporaryFile()
        self.f = h5py.File(tf.name, 'w')
        aa = self.f.create_dataset('avail', shape=(10, 10), dtype=np.bool)
        bb = self.f.create_dataset('data', shape=(10, 10), dtype=np.double)
        self.saw = SliceAvailableWrapper(aa, bb)

    def test_basics(self):
        self.saw[1, :] = np.arange(10)
        self.assertIsNotNone(self.saw[1, :])

    def test_deligate(self):
        self.assertEqual(self.saw.shape, (10, 10),
                         "Data.shape not correct is " + str(self.saw.shape))
        self.assertEqual(self.saw.dtype, np.double,
                         "Data.dtype not correct is " + str(self.saw.dtype))

    def tearDown(self):
        self.f.close()


class WrapperAlwaysAvailableTest(unittest.TestCase):

    def setUp(self):
        bb = np.random.rand(10, 10)
        self.saw = SliceAlwaysAvailableWrapper(bb)

    def test_basics(self):
        self.assertIsNotNone(self.saw[1, :])

    def test_deligate(self):
        self.assertEqual(self.saw.shape, (10, 10),
                         "Data.shape not correct is " + str(self.saw.shape))
        self.assertEqual(self.saw.dtype, np.double,
                         "Data.dtype not correct is " + str(self.saw.dtype))


class RawTimeseriesDataTest(unittest.TestCase):

    def setUp(self):
        self.data = tu.get_nexus_test_data()

    def test_get_clusterd_frame_list(self):
        frame_list = self.data.get_clusterd_frame_list()
        self.assertEqual(len(frame_list), 5,
                         "Length of framelist is actually %i"
                         % len(frame_list))
        self.assertEqual(frame_list[0].min(), 0,
                         "Start of region 0 is actually %i"
                         % frame_list[0].min())
        self.assertEqual(frame_list[1].min(), 5,
                         "Start of region 1 is actually %i"
                         % frame_list[1].min())
        self.assertEqual(frame_list[2].min(), 10,
                         "Start of region 2 is actually %i"
                         % frame_list[2].min())
        self.assertEqual(frame_list[3].min(), 101,
                         "Start of region 3 is actually %i"
                         % frame_list[3].min())
        self.assertEqual(frame_list[4].min(), 106,
                         "Start of region 4 is actually %i"
                         % frame_list[4].min())

    def tearDown(self):
        self.data.complete()

if __name__ == "__main__":
    unittest.main()
