# -*- coding: utf-8 -*-
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
.. module:: plugins_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest
import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner_no_process_list
from savu.test.travis.framework_tests.plugin_runner_test import \
        run_protected_plugin_runner


class AstraReconCpuTests(unittest.TestCase):
    global data_file, experiment
    data_file = '24737.nxs'
    experiment = 'tomo'

    def test_astra_recon_cpu(self):
        options = tu.initialise_options(None, 'tomo', None)
        plugin = 'savu.plugins.reconstructions.astra_recons.astra_recon_cpu'
        run_protected_plugin_runner_no_process_list(options, plugin)
        tu.cleanup(options)

    def test_astra_recon_init_vol(self):
        process_list = 'reconstruction/astra_init_vol_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

if __name__ == "__main__":
    unittest.main()
