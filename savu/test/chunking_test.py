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
.. module:: chunking_tests
   :platform: Unix
   :synopsis: checking the chunking for a variety of pattern transforms

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

import unittest
import tempfile
from savu.test import test_utils as tu

from savu.test.plugin_runner_test import run_protected_plugin_runner


class ChunkingTests(unittest.TestCase):

    def test_spectra_to_tomo(self):
        print "hello"
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('mm.nxs'),
            "process_file": tu.get_test_process_path('pyfai_tomo_chunking_test.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)

if __name__ == "__main__":
    unittest.main()
