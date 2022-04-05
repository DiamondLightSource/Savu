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

.. moduleauthor:: Nicola Wadespm <scientificsoftware@diamond.ac.uk>

"""

import unittest
from savu.test import test_utils as tu

from savu.test.travis.framework_tests.plugin_runner_test \
    import run_protected_plugin_runner
from savu.test.travis.framework_tests.plugin_runner_test \
    import run_protected_plugin_runner_no_process_list


class MultipleDatasetsTest(unittest.TestCase):

    def test_mm(self):
        data_file = tu.get_test_data_path('mm.nxs')
        process_file = tu.get_test_process_path('datasets/multiple_mm_inputs_test.nxs')
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

    def test_tomo1(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.basic_operations.basic_operations'
        data_dict = {'in_datasets': ['tomo', 'tomo'], 'out_datasets': ['test'],
                     'operations': ['tomo + tomo'],  'pattern': 'PROJECTION'}
        saver_dict = {}
        all_dicts = [{}, data_dict, saver_dict]
        run_protected_plugin_runner_no_process_list(options, plugin,
                                                    data=all_dicts)

    def test_tomo2(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.basic_operations.basic_operations'
        preview = ['10:-1:1:1', '10:-1:1:1', '10:-1:1:1']
        loader_dict = {'preview': preview}
        data_dict = {'in_datasets': ['tomo', 'tomo'], 'out_datasets': ['test'],
                     'operations': ['tomo + tomo'],  'pattern': 'PROJECTION'}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        self.assertEqual(exp.index['in_data']['test'].get_shape(),
                         (81, 125, 150))

    def test_tomo3(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.basic_operations.basic_operations'
        preview = ['10:-1:10:1', '10:-1:10:1', '10:-1:10:1']
        loader_dict = {'preview': preview}
        data_dict = {'in_datasets': ['tomo', 'tomo'], 'out_datasets': ['test'],
                     'operations': ['tomo + tomo'],  'pattern': 'PROJECTION'}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        exp = self.assertEqual(exp.index['in_data']['test'].get_shape(),
                               (9, 13, 15))

    def test_tomo4(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.basic_operations.basic_operations'
        preview = ['10:-10:10:1', '10:-10:10:1', '10:-10:10:1']
        loader_dict = {'preview': preview}
        data_dict = {'in_datasets': ['tomo', 'tomo'], 'out_datasets': ['test'],
                     'operations': ['tomo + tomo'],  'pattern': 'PROJECTION'}
        all_dicts = [loader_dict, data_dict, {}]
        exp = run_protected_plugin_runner_no_process_list(options, plugin,
                                                          data=all_dicts)
        exp = self.assertEqual(exp.index['in_data']['test'].get_shape(),
                               (8, 12, 15))

    def test_load_once_pass_data(self):
        """Load datasets and pass down list explicitly"""
        data_file = tu.get_test_data_path('tomo_standard.nxs')
        process_file = tu.get_test_process_path('datasets/ds_load_once.nxs')
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

    def test_pass_unspecified_data(self):
        """Load data, process data and save as a new dataset name,
        the last plugin processes an unspecified dataset (by default the first)"""
        data_file = tu.get_test_data_path('tomo_standard.nxs')
        process_file = tu.get_test_process_path('datasets/ds_unspecified_in_data.nxs')
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))




if __name__ == "__main__":
    unittest.main()
