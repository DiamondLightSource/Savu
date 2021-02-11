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
.. currentmodule:: savu

The Base level for Savu

use with :

import savu

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""


import os
import sys
from . import test
from unittest import defaultTestLoader, TestLoader, TextTestRunner

savuPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(savuPath + "/../lib"))
os.environ['savu_mode'] = 'hdf5'

def run_full_tests():
    import unittest

    print("Tests will run shortly, and may take some time to complete")
    print("The tests may raise errors, please don't worry about these as "
          "they may be raised deliberately.")
    print("The key information is in the final test results")

    path = os.path.split(test.travis.__file__)[0]
    tests = defaultTestLoader.discover(path, pattern='*test.py')
    testRunner = TextTestRunner(buffer=True)
    test_results = testRunner.run(tests)
    if test_results.wasSuccessful():
        exit(0)
    else:
        exit(1)

def run_tests():
    import unittest
    from savu.test.travis.plugin_tests.reconstruction_tests.tomo_pipeline_preview_test \
        import TomoPipelinePreviewTest
    print("Running a quick test...")
    tests = TestLoader().loadTestsFromTestCase(TomoPipelinePreviewTest)
    testRunner = TextTestRunner(verbosity=1, buffer=True)
    test_results = testRunner.run(tests)
    print("Test complete...")
    if test_results.wasSuccessful():
        exit(0)
    else:
        exit(1) 
