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
The Base level for Savu

use with :

import savu

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import os
import sys

savuPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(savuPath + "/../lib"))
# add xraylib
sys.path.append(os.path.join(savuPath + "/dls_sw/apps/xraylib/3.0.0/64/lib/python2.7/site-packages"))

def run_tests():
    import unittest
    from . import test

    path = os.path.split(test.__file__)[0]
    testmodules = ['savu.test.%s' % (os.path.splitext(p)[0]) for p in
                   os.listdir(path)]
    suite = unittest.TestSuite()

    for t in testmodules:
        try:
            mod = __import__(t, globals(), locals(), ['suite'])
            suitefn = getattr(mod, 'suite')
            suite.addTest(suitefn())
        except (ImportError, AttributeError):
            # else, just load all the test cases from the module.
            suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

    print "Tests will run shortly, and may take some time to complete"
    print "The tests may raise errors, please don't worry about these as " + \
        "they may be raised deliberatly"
    print "The key information is in the final test results"

    unittest.TextTestRunner().run(suite)
