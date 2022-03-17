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
   :synopsis: unittest test for tomobar 2D/3D (GPU) reconstruction software

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
        run_protected_plugin_runner

class TomobarGpuTest(unittest.TestCase):
    def setUp(self):
        self.data_file = 'tomo_standard.nxs'
        self.experiment = 'tomo'

    def test_tomobar_2drecon(self):
        process_list = 'reconstruction/tomobar/tomobar2d_gpu_recon.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_tomobar_swls_2drecon(self):
        process_list = 'reconstruction/tomobar/tomobar2d_SWLS_gpu_recon.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)
    """
    def test_tomobar3d_full(self):
        process_list = 'reconstruction/tomobar/tomobar_fully3d_gpu_recon.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)
    """
    def test_tomobar3d_fast(self):
        process_list = 'reconstruction/tomobar/tomobar3d_gpu_recon.nxs'
        options1 = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options1)

        #read the output file using SavuNexusLoader
        data_file2 = options1['out_path'] + 'test_processed.nxs'
        options2 = tu.initialise_options(data_file2, 'load_data', 'loaders/savu_nexus_loader_test4.nxs')
        run_protected_plugin_runner(options2)
        tu.cleanup(options1)
        tu.cleanup(options2)

    def test_tomobar3d_FBP_alignment(self):
        process_list = 'reconstruction/tomobar/iterative_alignment_tomobar3d_FBP_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_tomobar3d_FISTA_alignment(self):
        process_list = 'reconstruction/tomobar/iterative_alignment_tomobar3d_FISTA_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

if __name__ == "__main__":
    unittest.main()
