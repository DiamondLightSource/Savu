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
.. module:: plugins_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import unittest

from savu.test.plugin_test import PluginTest


class CglsReconTest(PluginTest):
    
    def setUp(self):
        self.plugin_name = "savu.plugins.cgls_recon"

if __name__ == "__main__":
    unittest.main()
