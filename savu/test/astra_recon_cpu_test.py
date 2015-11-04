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
from savu.test.plugin_runner_test import run_protected_plugin_runner
import savu.plugins.reconstructions.astra_recons as astra_recons

class PluginRunnerAstraReconCPUTest(unittest.TestCase):

    def test_astra_recon_cpu(self):
        options = tu.set_experiment('tomo')
        plugin = astra_recons.__name__ + '.astra_recon_cpu'
        tu.set_plugin_list(options, plugin)
        run_protected_plugin_runner(options)

if __name__ == "__main__":
    unittest.main()
