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
.. module:: data_test
   :platform: Unix
   :synopsis: unittest test class data structures

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest

import savu.test.test_utils as tu
import savu.plugins.utils as pu


class Test(unittest.TestCase):

    def test_create_smaller_data_block(self):
        data = tu.get_nx_tomo_test_data()
        plugin = pu.load_plugin("savu.plugins.downsample_filter")
        output = tu.get_appropriate_output_data(plugin, data)[0]
        self.assertEqual(output.get_data_shape(), (111, 68, 80))

if __name__ == "__main__":
    unittest.main()
