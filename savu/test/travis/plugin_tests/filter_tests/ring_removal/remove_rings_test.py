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
.. module:: Remove stripe artefacts (ring removal)
   :platform: Unix
   :synopsis: runner for tests using the MPI framework
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>
"""
import unittest
import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
        run_protected_plugin_runner

class RemoveRingsTest(unittest.TestCase):
    global data_file, experiment
    data_file = '24737.nxs'
    experiment = 'tomo'

    def test_remove_large_rings(self):
        process_list = 'filters/ring_removal/ring_removal_large_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_ring_removal_filtering(self):
        process_list = 'filters/ring_removal/ring_removal_filtering_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_ring_removal_fitting(self):
        process_list = 'filters/ring_removal/ring_removal_fitting_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_ring_removal_normalization(self):
        process_list = 'filters/ring_removal/ring_removal_normalization_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_ring_removal_regularization(self):
        process_list = 'filters/ring_removal/ring_removal_regularization_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_ring_removal_sorting(self):
        process_list = 'filters/ring_removal/ring_removal_sorting_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_remove_unresponsive_fluctuating_rings(self):
        process_list = 'filters/ring_removal/remove_unresponsive_fluctuating_rings_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_remove_all_rings(self):
        process_list = 'filters/ring_removal/remove_all_rings_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_ring_removal_waveletfft(self):
        process_list = 'filters/ring_removal/ring_removal_waveletfft_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_raven_filter(self):
        process_list = 'filters/ring_removal/raven_filter_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_ccpi_ring_artefact_filter(self):
        process_list = 'filters/ring_removal/ccpi_ring_artefact_filter_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_ring_removal_interpolation(self):
        process_list = 'filters/ring_removal/ring_removal_interpolation_test.nxs'
        options = tu.initialise_options(data_file, experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

if __name__ == "__main__":
    unittest.main()
