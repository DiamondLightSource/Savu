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
#import tempfile

import savu.test.test_utils as tu
from savu.test.plugin_runner_test \
    import run_protected_plugin_runner_no_process_list


class I12DataMappingTest(unittest.TestCase):

    @unittest.skip('takes too long to run')
    def test_i12tomo(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [{}, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (901, 2160, 2560, 24))

    # should send each frame separately and not grouped
    def test_i12tomo2(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['midmap:midmap+1:endmap:5', '0:end:1:1', '0:end:1:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (5, 2160, 2560, 1))

    def test_i12tomo3(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['midmap:4*endmap:endmap:5', '0:end:10:1', '0:end:10:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (5, 216, 256, 4))

    def test_i12tomo4(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['midmap:4*endmap:endmap:1', '0:end:10:1', '0:end:10:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (1, 216, 256, 4))

    def test_i12tomo5(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['0:20:1:1', '0:-1:5:1', '0:-1:5:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (20, 432, 512, 1))

    def test_i12tomo6(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['midmap:end:endmap:5', '0:end:10:1', '0:end:10:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (5, 216, 256, 24))

    def test_i12tomo7(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['mid-2:mid+2:1:1', '0:end:10:1', '0:end:10:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (2, 216, 256, 2))

    def test_i12tomo8(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['0:endmap:20:1', '0:end:1:1', '0:end:1:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (46, 2160, 2560, 1))

    @unittest.skip('takes too long to run')
    def test_i12tomo9(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['0:end:1:1', '0:end:30:1', '0:end:300:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (901, 72, 9, 24))


if __name__ == "__main__":
    unittest.main()
