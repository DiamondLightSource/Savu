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
.. module:: alignment_test
   :platform: Unix
   :synopsis: Test for iterative alignment pipeline.

.. moduleauthor:: Yousef Moazzam <scientificsoftware@diamond.ac.uk>

"""

import unittest
import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class AlignmentTest(unittest.TestCase):
    def setUp(self):
        self.data_file = 'tomo_standard.nxs'
        self.experiment = 'tomo'

    def test_iterative_alignment_cpu_pipeline(self):
        # TODO: the process list uses TomoPhantomLoader to generate projections
        # for the reconstruction, maybe should be replaced with real data at
        # some point to avoid extra plugin dependencies
        process_list = 'iterative_alignment_cpu_pipeline.nxs'
        options = tu.initialise_options(self.data_file, self.experiment,
                                        process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)