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
.. module:: nx_xrd_loader_test
   :platform: Unix
   :synopsis: testing the nx_xrd loader

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class I13PtychoLoaderTest(unittest.TestCase):

    @unittest.skip('Skipping due to permissions error on data folder')
    def test_i13_ptycho(self):
#         data_file = '/dls/i13-1/data/2016/mt14190-1/processing/tomo_processed/ptycho/ptycho_vds_testeroo.h5'
        data_file = '/dls/science/users/clb02321/DAWN_stable/I13Test_Catalysts/processing/catalyst_data/stacked_data/ptycho_tomo_copied_92713.h5'
        process_file = '/dls/science/users/clb02321/DAWN_stable/Savu2/Savu/test_data/test_process_lists/basic_ptycho_process_i13.nxs'
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))

if __name__ == "__main__":
    unittest.main()
