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
.. module:: savu_nexus_loader_test
   :platform: Unix
   :synopsis: test re-loading of savu output data
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner
import tempfile
import os

class SavuNexusLoaderTest(unittest.TestCase):
    global data_file, experiment
    data_file = '24737.nxs'
    experiment = None

    def test_reload(self):
        process_list = 'loaders/savu_nexus_loader_test1.nxs'
        options1 = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options1)

        #read the output file using SavuNexusLoader
        data_file2 = options1['out_path'] + 'test_processed.nxs'
        options2 = tu.initialise_options(data_file2, 'load_data', 'loaders/savu_nexus_loader_test2.nxs')
        run_protected_plugin_runner(options2)
        tu.cleanup(options1)
        tu.cleanup(options2)

if __name__ == "__main__":
    unittest.main()
