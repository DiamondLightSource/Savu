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
.. module:: data_test
   :platform: Unix
   :synopsis: unittest test class data structures

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest

import savu.test.test_utils as tu
from savu.core.plugin_runner import PluginRunner


class Test(unittest.TestCase):

    def test_create_smaller_data_block(self):
        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.reshape.downsample_filter'
        tu.set_plugin_list(options, plugin)

        out_data_name = options['plugin_list'][1]['data']['out_datasets'][0]
        plugin_runner = PluginRunner(options)
        exp = plugin_runner._run_plugin_list()

        self.assertEqual(exp.index['in_data'][out_data_name].get_shape(),
                         (91, 45, 54))

if __name__ == "__main__":
    unittest.main()
