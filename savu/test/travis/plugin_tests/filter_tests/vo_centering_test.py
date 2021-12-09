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
.. module:: vo_centering_test
   :platform: Unix
   :synopsis: unittest for vo centering routine

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class VoCenterTest(unittest.TestCase):

    def test_vo_centering(self):
        data_file = tu.get_test_data_path('tomo_standard.nxs')
        plist = 'vo_centering_test/vo_centering_test.nxs'
        process_file = tu.get_test_process_path(plist)
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

    def test_vo_centering_single_sino_loader(self):
        data_file = tu.get_test_data_path('tomo_standard.nxs')
        plist = 'vo_centering_test/vo_centering_single_sino_loader_test.nxs'
        process_file = tu.get_test_process_path(plist)
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

    def test_vo_centering_single_sino_centering(self):
        data_file = tu.get_test_data_path('tomo_standard.nxs')
        plist = 'vo_centering_test/vo_centering_single_sino_centering_test.nxs'
        process_file = tu.get_test_process_path(plist)
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

    def test_vo_centering_single_sinos(self):
        data_file = tu.get_test_data_path('tomo_standard.nxs')
        plist = 'vo_centering_test/vo_centering_single_sinos_test.nxs'
        process_file = tu.get_test_process_path(plist)
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

if __name__ == "__main__":
    unittest.main()
