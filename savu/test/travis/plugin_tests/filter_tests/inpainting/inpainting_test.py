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
.. module:: inpainting_test
   :platform: Unix
   :synopsis: Tests for the inpainting plugin

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner_no_process_list
from savu.test.travis.framework_tests.plugin_runner_test import \
        run_protected_plugin_runner

class InpaintingTest(unittest.TestCase):
    global data_file, experiment
    data_file = 'tomo_standard.nxs'
    experiment = 'tomo'

    def test_inpainting_sinogram(self):
        process_list = 'filters/inpainting/inpainting_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

if __name__ == "__main__":
    unittest.main()
