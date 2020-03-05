# Copyright 2020 Rosalind Franklin Institute.
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
.. module:: mrc_loader_test
   :platform: Unix
   :synopsis: test loading of mrc data
.. moduleauthor:: Mark Basham <mark.basham@rfi.ac.uk>

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class SavuNexusLoaderTest(unittest.TestCase):

    def test_reload(self):
        data_file = tu.get_test_data_path('test_image.mrc')
        process_file = tu.get_test_process_path('mrc_loader_test.nxs')
        run_protected_plugin_runner(
                tu.set_options(data_file, process_file=process_file))


if __name__ == "__main__":
    unittest.main()
