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
.. module:: dezinger_test
   :platform: Unix
   :synopsis: Tests for the dezinger plugin

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner_no_process_list
from savu.test.travis.framework_tests.plugin_runner_test import \
        run_protected_plugin_runner
import savu.test.base_checkpoint_test
import tempfile
import os


class DezingerTest(unittest.TestCase):

    def test_dezing_filter(self):
        self.test_folder = tempfile.mkdtemp(suffix='my_test/')
        options = tu.set_experiment('tomoRaw')
        options['out_path'] = os.path.join(self.test_folder)
        plugin = 'savu.plugins.filters.dezinger_simple'
        run_protected_plugin_runner_no_process_list(options, plugin)

        # perform folder cleaning
        classb = savu.test.base_checkpoint_test.BaseCheckpointTest()
        cp_folder = os.path.join(self.test_folder, 'checkpoint')
        classb._empty_folder(cp_folder)
        os.removedirs(cp_folder)
        classb._empty_folder(self.test_folder)
        os.removedirs(self.test_folder)

    def test_dezinger(self):
        data_file = tu.get_test_data_path('24737.nxs')
        self.test_folder = tempfile.mkdtemp(suffix='my_test/')
        # set options
        options = tu.set_experiment('tomo')
        options['data_file'] = data_file
        options['out_path'] = os.path.join(self.test_folder)
        options['process_file'] = tu.get_test_process_path('dezinger/dezinger_test.nxs')
        run_protected_plugin_runner(options)

        # perform folder cleaning
        classb = savu.test.base_checkpoint_test.BaseCheckpointTest()
        cp_folder = os.path.join(self.test_folder, 'checkpoint')
        classb._empty_folder(cp_folder)
        os.removedirs(cp_folder)
        classb._empty_folder(self.test_folder)
        os.removedirs(self.test_folder)

    def test_dezinger_sinogram(self):
        data_file = tu.get_test_data_path('24737.nxs')
        self.test_folder = tempfile.mkdtemp(suffix='my_test/')
        # set options
        options = tu.set_experiment('tomo')
        options['data_file'] = data_file
        options['out_path'] = os.path.join(self.test_folder)
        options['process_file'] = tu.get_test_process_path('dezinger/dezinger_sinogram_test.nxs')
        run_protected_plugin_runner(options)

        # perform folder cleaning
        classb = savu.test.base_checkpoint_test.BaseCheckpointTest()
        cp_folder = os.path.join(self.test_folder, 'checkpoint')
        classb._empty_folder(cp_folder)
        os.removedirs(cp_folder)
        classb._empty_folder(self.test_folder)
        os.removedirs(self.test_folder)

if __name__ == "__main__":
    unittest.main()
