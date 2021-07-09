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
import subprocess

savuPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(savuPath + "/../lib"))
os.environ['savu_mode'] = 'hdf5'

def run_refresh_lists():
    print("This function will refresh all process lists")
    result = subprocess.run(["python", savuPath+'/../scripts/configurator_tests/refresh_process_lists_test.py'])
    if (result.returncode == 1):
        print("Tests FAILED, please see the report")
        exit(1)
    else:
        print("Tests PASSED")
        exit(0)

def run_full_tests():

    print("Tests may take some time to complete...")
    print("The tests may raise errors, please don't worry about these as "
          "they may be raised deliberately.")
    path = os.path.split(test.travis.__file__)[0]
    result2 = subprocess.run(["pytest", path+'/../../../scripts/configurator_tests/savu_config_test.py'])
    result = subprocess.run(["python", path+'/tests.py'])
    if ((result.returncode == 1) or (result2.returncode == 1)):
        print("Tests FAILED, please see the report")
        exit(1)
    else:
        print("Tests PASSED")
        exit(0)

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
