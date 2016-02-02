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

from savu.test.plugin_runner_test import run_protected_plugin_runner


# @unittest.skip('functions are currently being updated')
class I18PipelineTest(unittest.TestCase):
#     def test1(self):
#         options = {
#             "transport": "hdf5",
#             "process_names": "CPU0",
#             "data_file": tu.get_test_data_path('mm.nxs'),
#             "process_file": '/dls/i13/data/2015/cm12165-5/processing/AskAaron/playwithclusteranalysis/I18_pipeline_just_xrd_from_raw_filtered_58905.nxs',
#             "out_path": tempfile.mkdtemp()
#             }
#         run_protected_plugin_runner(options)
#         
#     def test2(self):
#         options = {
#             "transport": "hdf5",
#             "process_names": "CPU0",
#             "data_file": tu.get_test_data_path('mm.nxs'),
#             "process_file": '/dls/i13/data/2015/cm12165-5/processing/AskAaron/playwithclusteranalysis/I18_pipeline_just_xrd_from_raw_filtered_58905.nxs',
#             "out_path": tempfile.mkdtemp()
#             }
#         run_protected_plugin_runner(options)

    def test_xrdtomo(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('mm.nxs'),
            "process_file": tu.get_test_process_path('pyfai_tomo_chunking_test.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)
# 
#     def test_noxrdtomo(self):
#         options = {
#             "transport": "hdf5",
#             "process_names": "CPU0",
#             "data_file": tu.get_test_data_path('mm.nxs'),
#             "process_file": tu.get_process_list_path('I18_pipeline_noxrd.nxs'),
#             "out_path": tempfile.mkdtemp()
#             }
#         run_protected_plugin_runner(options)
# 
#     def test_noxrdtomo_scikit(self):
#         options = {
#             "transport": "hdf5",
#             "process_names": "CPU0",
#             "data_file": tu.get_test_data_path('mm.nxs'),
#             "process_file": tu.get_process_list_path('I18_pipeline_noxrd_scikit.nxs'),
#             "out_path": tempfile.mkdtemp()
#             }
#         run_protected_plugin_runner(options)

#     def test_full(self):
#         options = {
#             "transport": "hdf5",
#             "process_names": "CPU0",
#             "data_file": tu.get_test_data_path('mm.nxs'),
#             "process_file": tu.get_process_list_path('I18_pipeline_just_xrd.nxs'),
#             "out_path": tempfile.mkdtemp()
#             }
#         run_protected_plugin_runner(options)
#     def test_process(self):
#         options = {
#             "transport": "hdf5",
#             "process_names": "CPU0",
#             "data_file": tu.get_test_data_path('mm.nxs'),
#             "process_file": tu.get_test_process_path('I18_pipeline.nxs'),
#             "out_path": tempfile.mkdtemp()
#             }
#         run_protected_plugin_runner(options)
if __name__ == "__main__":
    unittest.main()
