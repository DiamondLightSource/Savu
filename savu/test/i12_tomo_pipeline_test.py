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


class I12TomoPipelineTest(unittest.TestCase):

    # should send each frame separately and not grouped
    def test_i12pipeline(self):
        options = tu.set_experiment('i12tomo')
        plugin = 'savu.plugins.corrections.i12_dark_flat_field_correction'
        selection = ['midmap:midmap+1:endmap:4', '0:end:1:1', '0:end:1:1']
        loader_dict = {'preview': selection}
        data_dict = {'in_datasets': ['tomo'], 'out_datasets': ['test']}
        all_dicts = [loader_dict, data_dict, {}]
        run_protected_plugin_runner_no_process_list(options, plugin,
                                                    data=all_dicts)

if __name__ == "__main__":
    unittest.main()
