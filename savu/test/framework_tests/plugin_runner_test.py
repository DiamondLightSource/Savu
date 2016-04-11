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
import tempfile
from savu.test import test_utils as tu
import savu.plugins.utils as pu
from savu.core.plugin_runner import PluginRunner


def run_protected_plugin_runner_no_process_list(options, plugin, **kwargs):
    pu.datasets_list = []
    try:
        if 'data' in kwargs.keys():
            tu.set_plugin_list(options, plugin, kwargs['data'])
        else:
            tu.set_plugin_list(options, plugin)
        plugin_runner = PluginRunner(options)
        exp = plugin_runner._run_plugin_list()
        return exp
    except ImportError as e:
        print("Failed to run test as libraries not available (%s)," % (e) +
              " passing test")
        pass


def run_protected_plugin_runner(options):
    pu.datasets_list = []
    try:
        plugin_runner = PluginRunner(options)
        exp = plugin_runner._run_plugin_list()
        return exp
    except ImportError as e:
        print("Failed to run test as libraries not available (%s)," % (e) +
              " passing test")
        pass


if __name__ == "__main__":
    unittest.main()
