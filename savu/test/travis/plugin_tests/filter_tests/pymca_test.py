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
.. module:: pymca_test
   :platform: Unix
   :synopsis: testing the simple fit plugin
.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class PymcaTest(unittest.TestCase):
    def test_simple_fit_runs(self):
#         data_file = '/dls/i13-1/data/2016/mt14190-1/raw/91318.nxs'#
        data_file = tu.get_test_data_path('i18_test_data.nxs')
        process_file = tu.get_test_process_path('pymca_test.nxs')
#         process_file = '/dls/i13-1/data/2016/mt14190-1/processing/savu/process_lists/pymca_process.nxs'
        options = tu.set_options(data_file, process_file=process_file)
        self.datapath = options['out_path']
        run_protected_plugin_runner(options)


if __name__ == "__main__":
    unittest.main()
