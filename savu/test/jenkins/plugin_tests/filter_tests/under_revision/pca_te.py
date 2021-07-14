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
.. module:: pca_te
   :platform: Unix
   :synopsis: Test all the component analyses

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>

"""

import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class PcaTest(unittest.TestCase):

    def test_process(self):
        data_file = tu.get_test_big_data_path('xrd_tomo_p3_astra_recon_cpu.h5')
        process_file = tu.get_test_process_path('to_revise/pca_test.nxs')
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

if __name__ == "__main__":
    unittest.main()
