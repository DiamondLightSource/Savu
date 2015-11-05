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
.. module:: tomo_recon
   :platform: Unix
   :synopsis: runner for tests using the MPI framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import unittest
from savu.test import test_utils as tu

from savu.test.plugin_runner_test import \
    run_protected_plugin_runner_no_process_list


class PluginRunnerScikitImageTest(unittest.TestCase):

    def test_fbp(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.reconstructions.' + \
            'scikitimage_filter_back_projection'
        run_protected_plugin_runner_no_process_list(options, plugin)

    def test_sart(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.reconstructions.scikitimage_sart'
        run_protected_plugin_runner_no_process_list(options, plugin)

if __name__ == "__main__":
    unittest.main()
