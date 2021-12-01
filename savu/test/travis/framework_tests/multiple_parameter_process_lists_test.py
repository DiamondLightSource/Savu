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
    run_protected_plugin_runner


class MultipleParameterProcessListTests(unittest.TestCase):

    def test_multi_params_tomo(self):
        data_file = tu.get_test_data_path('tomo_standard.nxs')
        process_file = tu.get_test_process_path(
            'basic_tomo_process_preview_params_test.nxs')
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

#    def test_multi_params_i12tomo(self):
#        process = 'i12_tomo_pipeline_test.nxs'
#        options = {
#            "transport": "hdf5",
#            "process_names": "CPU0",
#            "data_file": tu.get_test_data_path(
#                'i12_test_data/i12_test_data.nxs'),
#            "process_file": tu.get_test_process_path(process),
#            "out_path": tempfile.mkdtemp()
#            }
#        run_protected_plugin_runner(options)

if __name__ == "__main__":
    unittest.main()
