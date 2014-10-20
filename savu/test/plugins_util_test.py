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
.. module:: plugins_util_test
   :platform: Unix
   :synopsis: unittest test class for plugin utils

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest

from savu.plugins import utils as pu
from savu.plugins import plugin as test_plugin


class Test(unittest.TestCase):

    def testGetPlugin(self):
        plugin = pu.load_plugin("savu.plugins.plugin")
        self.assertEqual(plugin.__class__, test_plugin.Plugin,
                         "Failed to load the correct class")
        self.assertRaises(NotImplementedError, plugin.process,
                          "test", "test", 1, 1)
        self.assertRaises(NotImplementedError, plugin.required_data_type)

if __name__ == "__main__":
    unittest.main()
