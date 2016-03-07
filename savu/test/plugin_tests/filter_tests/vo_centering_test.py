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
.. module:: vo_centering_test
   :platform: Unix
   :synopsis: unittest for vo centering routine

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest
import tempfile
from savu.test import test_utils as tu

from savu.test.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


@unittest.skip('Runs as a standalone test but not in the suite. Error to be investigated')
class VoCenterTest(unittest.TestCase):

    def test_vo_centering(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('24737.nxs'),
            "process_file": tu.get_test_process_path(
                'vo_centering_test.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)

#    def test_vo_centering(self):
#        options = tu.set_experiment('tomo')
#        plugin = 'savu.plugins.filters.vo_centering'
#        run_protected_plugin_runner_no_process_list(options, plugin)

#    def test_vo_centering_process(self):
#        options = {
#            "transport": "hdf5",
#            "process_names": "CPU0",
#            "data_file": tu.get_test_data_path('tomo'),
#            "process_file": tu.get_test_process_path(
#                'vo_centering_process.nxs'),
#            "out_path": tempfile.mkdtemp()
#            }
#        run_protected_plugin_runner(options)
#
#    def test_multimodal_process(self):
#        options = {
#            "transport": "hdf5",
#            "process_names": "CPU0",
#            "data_file": tu.get_test_data_path('mm.nxs'),
#            "process_file": tu.get_test_process_path(
#                'vo_centering_multimodal_process.nxs'),
#            "out_path": tempfile.mkdtemp()
#            }
#        run_protected_plugin_runner(options)

if __name__ == "__main__":
    unittest.main()
