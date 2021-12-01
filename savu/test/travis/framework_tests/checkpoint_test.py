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
.. module:: checkpoint_tests
   :platform: Unix
   :synopsis: Checking Savu checkpointing works correctly

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import unittest
from savu.test import test_utils as tu
from savu.test.base_checkpoint_test import BaseCheckpointTest


class CheckpointTest(BaseCheckpointTest, unittest.TestCase):

    def setUp(self):
        super(CheckpointTest, self).setUp()

    def tearDown(self):
        super(CheckpointTest, self).tearDown()

    def set_plist(self, exp):
        plist = exp.meta_data.plugin_list.plugin_list
        plist = [p['name'] for p in plist[1:]]
        plist[-1] = 'final_result_tomo'
        return plist

    def set_data_options(self):
        options = tu.set_options(tu.get_test_data_path('tomo_standard.nxs'))
        options['process_file'] = \
            tu.get_test_process_path('checkpoint_process2.nxs')
        return options

if __name__ == "__main__":
    unittest.main()
