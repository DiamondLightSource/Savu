# -*- coding: utf-8 -*-
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
.. module:: refresh_process_lists_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import os
import unittest
import savu.test.test_utils as tu
import scripts.config_generator.config_utils as cu
from scripts.config_generator.content import Content


class RefreshProcessListsTest(unittest.TestCase):

    def test_refresh(self):
        cu.populate_plugins()
        path = os.path.dirname(os.path.realpath(__file__)).split('scripts')[0]
        test_path = path + '/test_data/test_process_lists'
        nxs_files = tu.get_test_process_list(test_path)
        exclude = ['new_fittest.nxs', 'ptycho_ptypy_compact_test.nxs']
        for f in nxs_files:
            if f not in exclude:
                print f
                self._refresh_process_file(os.path.join(test_path, f))

    def _refresh_process_file(self, path):
        content = Content()
        # open
        content.fopen(path, update=True)
        # refresh
        positions = content.get_positions()
        for pos_str in positions:
            content.refresh(pos_str)
        # save
        content.save(content.filename)


if __name__ == "__main__":
    unittest.main()
