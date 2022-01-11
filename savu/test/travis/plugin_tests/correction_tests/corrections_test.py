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
.. module:: corrections_test
   :platform: Unix
   :synopsis: Tests for correction plugins

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner

class CorrectionsTest(unittest.TestCase):
    
    def setUp(self):
        self.data_file = 'tomo_standard.nxs'
        self.experiment = None

    def test_camera_rot_correction(self):
        process_list = 'corrections/camera_rot_corr_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment,
                                        process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_subpixel_shift(self):
        process_list = 'corrections/subpixel_shift_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment,
                                        process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_time_based_correction(self):
        process_list = 'corrections/time_based_correction_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment,
                                        process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_time_based_correction2(self):
        process_list = 'corrections/time_based_correction_test2.nxs'
        options = tu.initialise_options(self.data_file, self.experiment,
                                        process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_mtf_deconvolution(self):
        process_list = 'corrections/mtf_deconvolution_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment,
                                        process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_convert_360_180_sinogram(self):
        process_list = 'corrections/convert_360_180_sinogram_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment,
                                        process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

if __name__ == "__main__":
    unittest.main()