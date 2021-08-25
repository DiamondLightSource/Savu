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

class DezingerTest(unittest.TestCase):
    def setUp(self):
        self.data_file = '24737.nxs'
        self.experiment = 'tomo'

    #def test_dezing_filter(self):
    #    options = tu.initialise_options(None, 'tomoRaw', None)
    #    plugin = 'savu.plugins.filters.dezinger_simple'
    #    run_protected_plugin_runner_no_process_list(options, plugin)
    #    tu.cleanup(options)

    def test_dezinger_sinogram(self):
        process_list = 'filters/dezinger/dezinger_sinogram_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)
        
    def test_dezinger(self):
        process_list = 'filters/dezinger/dezinger_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)              

        
if __name__ == "__main__":
    unittest.main()
