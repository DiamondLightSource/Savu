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
.. module:: map3dto4d_pipeline_test
   :platform: Unix
   :synopsis: Test for 3d to 4d tomography processing pipeline.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import unittest
import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class Map3dto4dPipelineTest(unittest.TestCase):
    global data_file, experiment
    data_file = '/i12_test_data/i12_test_data.nxs'
    experiment = None

    def test_process_preview(self):
        process_list = 'map3dto4d_pipeline_preview_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)               

    def test_process_preview_2d_angles(self):
        process_list = 'map3dto4d_pipeline_preview_test_2d_angles.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)  

#    def test_process(self):
#        data_file = tu.get_test_data_path('/i12_test_data/i12_test_data.nxs')
#        process_file = tu.get_test_process_path('i12_tomo_pipeline_test.nxs')
#        run_protected_plugin_runner(tu.set_options(data_file,
#                                                   process_file=process_file))

if __name__ == "__main__":
    unittest.main()
