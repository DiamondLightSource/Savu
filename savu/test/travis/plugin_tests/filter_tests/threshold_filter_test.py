# -*- coding: utf-8 -*-
# Copyright 2016 Diamond Light Source Ltd.
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
.. module:: Threshold filter test
   :platform: Unix
   :synopsis: unittest test classes for quantisation plugin

.. moduleauthor:: Nicoletta De Maio <scientificsoftware@diamond.ac.uk>

"""

import unittest

import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class ThresholdFilterTest(unittest.TestCase):
    global data_file, experiment
    data_file = 'tomo_standard.nxs'
    experiment = None

    def test_binary_quantisation_filter(self):
        process_list = 'threshold_filter_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

if __name__ == "__main__":
    unittest.main()
