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
.. module:: ListToProjectionsTest
   :platform: Unix
   :synopsis: Test all the component analyses

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>

"""

import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class ListToProjectionsTest(unittest.TestCase):
#     @unittest.skip('Something is up with this')
    def test_process(self):
        path = '/dls/science/users/clb02321/DAWN_stable/I13Test_Catalysts/processing/catalyst_data/analysis92713/'
        data_file = path+'20170222134626_ptycho_tomo_copied_92713/fluo_p1_pymca.h5'
        process_file = path+'interpolation_test.nxs'
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

if __name__ == "__main__":
    unittest.main()
