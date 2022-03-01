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
.. module:: filter_test
   :platform: Unix
   :synopsis: Test for iterating filter plugins.

.. moduleauthor:: Yousef Moazzam <scientificsoftware@diamond.ac.uk>

"""

import unittest
import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class FilterTest(unittest.TestCase):
    def setUp(self):
        self.data_file = 'tomo_standard.nxs'
        self.experiment = 'tomo'

    # TODO: the process lists in these tests all use TomoPhantomLoader and
    # TomoPhantomArtifacts to apply noise, maybe should be replaced with real
    # data at some point to avoid extra plugin dependencies
    def test_iterate_one_median_filter(self):
        process_list = 'iterate_one_median_filter.nxs'
        options = tu.initialise_options(self.data_file, self.experiment,
                                        process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_iterate_three_median_filters(self):
       process_list = 'iterate_three_median_filters.nxs'
       options = tu.initialise_options(self.data_file, self.experiment,
                                     process_list)
       run_protected_plugin_runner(options)
       tu.cleanup(options)

    def test_iterate_two_ccpi_denosiing_cpu_pattern_switching(self):
       process_list = 'iterate_two_ccpi_denosiing_cpu_pattern_switching.nxs'
       options = tu.initialise_options(self.data_file, self.experiment,
                                     process_list)
       run_protected_plugin_runner(options)
       tu.cleanup(options)