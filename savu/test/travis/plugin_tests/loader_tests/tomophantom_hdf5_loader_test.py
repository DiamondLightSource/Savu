# -*- coding: utf-8 -*-
# Copyright 2020 Diamond Light Source Ltd.
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
.. module:: tomophantom_loader_test
   :platform: Unix
   :synopsis: unittest for the tomophantom loader

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""

import unittest
import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
        run_protected_plugin_runner

class TomophantomHdf5LoaderTest(unittest.TestCase):
    def setUp(self):
        self.data_file = 'tomo_standard.nxs'
        self.data_file2 = 'synthetic_data/synthetic_data.nxs'
        self.experiment = 'tomo'

    def test_tomophantom_loader(self):
        process_list = 'loaders/tomophantom_loader.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_loading_synth_proj_with_nxtomoloader(self):
        process_list = 'loaders/nxtomo_loading_synth_proj.nxs'
        options = tu.initialise_options(self.data_file2, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_loading_phantom_with_savunexusloader(self):
        process_list = 'loaders/savu_nexus_loading_phantom.nxs'
        options = tu.initialise_options(self.data_file2, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

if __name__ == "__main__":
    unittest.main()
