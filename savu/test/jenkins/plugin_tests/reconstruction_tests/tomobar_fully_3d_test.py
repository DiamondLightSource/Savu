# -*- coding: utf-8 -*-
# Copyright 2018 Diamond Light Source Ltd.
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
.. module:: plugins_test
   :platform: Unix
   :synopsis: unittest test for tomobar 3d (full) reconstruction software

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""

import unittest

import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner
import savu.test.base_checkpoint_test
import tempfile
import os

class TomobarFully3dTest(unittest.TestCase):

    def test_tomobar3d(self):
        data_file = tu.get_test_data_path('24737.nxs')
        self.test_folder = tempfile.mkdtemp(suffix='my_test/')
        # set options
        options = tu.set_experiment('tomo')
        options['data_file'] = data_file
        options['out_path'] = os.path.join(self.test_folder)
        options['process_file'] = tu.get_test_process_path('tomobar_fully3d_recon.nxs')
        run_protected_plugin_runner(options)

        #read the file using SavuNexusLoader
        path_to_rec = self.test_folder + 'test_processed.nxs'
        self.test_folder2 = tempfile.mkdtemp(suffix='my_test2/')
        print(self.test_folder2)
        options['data_file'] = path_to_rec
        options['out_path'] = os.path.join(self.test_folder2)
        options['process_file'] = tu.get_test_process_path('savu_nexus_loader_test3.nxs')
        run_protected_plugin_runner(options)
        
        # perform cleaning (to add)

if __name__ == "__main__":
    unittest.main()
