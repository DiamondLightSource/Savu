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
.. module:: i12 tomography test run
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import unittest
import tempfile

import savu.test.test_utils as tu
from savu.test.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class I12TomoPipelineTest(unittest.TestCase):

#    def test_i12pipeline(self):
#        options = tu.set_experiment('i12tomo')
#        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
#        selection = ['200:endmap-200:1:1', 'mid-2:mid+3:1:1',
#                     '800:end-800:1:1']
#        loader_dict = {'preview': selection}
#        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
#        all_dicts = [loader_dict, data_dict, {}]
#        run_protected_plugin_runner_no_process_list(options, plugin,
#                                                    data=all_dicts)

    def test_process_preview(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path(
                '/i12_test_data/i12_test_data.nxs'),
            "process_file": tu.get_test_process_path(
                'i12_tomo_pipeline_preview_test.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)

    def test_process(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path(
                '/i12_test_data/i12_test_data.nxs'),
            "process_file": tu.get_test_process_path(
                'i12_tomo_pipeline_test.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)

if __name__ == "__main__":
    unittest.main()
