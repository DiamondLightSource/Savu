# -*- coding: utf-8 -*-
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
.. module:: astra_multiple_parameter_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import unittest

import savu.plugins.utils as pu
import savu.test.test_utils as tu

from collections import OrderedDict


class AstraMultipleParameterTest(unittest.TestCase):

    def plugin_setup(self):
        ppath = 'savu.plugins.reconstructions.astra_recons.astra_recon_cpu'
        plugin = pu.load_class(ppath)()
        tools = plugin.get_plugin_tools()
        tools._populate_default_parameters()
        return plugin

    def framework_options_setup(self):
        key1 = 'n_iterations'
        key2 = 'algorithm'
        key3 = 'in_datasets'
        key4 = 'out_datasets'
        params = OrderedDict({key1: '1;2;3', key2: 'FBP;CGLS', key3: ['tomo'], key4: ['tomo']})

        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.reconstructions.astra_recons.astra_recon_cpu'
        tu.set_plugin_list(options, plugin, [{}, params, {}])
        return options

    def test_parameter_space_int(self):
        plugin = self.plugin_setup()
        key = 'n_iterations'
        params = {key: '1;2;3'}
        plugin.tools.set_plugin_list_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, [1, 2, 3])
        self.assertEqual(plugin.get_plugin_tools().extra_dims[0], 3)

    def test_parameter_space_str(self):
        plugin = self.plugin_setup()
        key = 'algorithm'
        params = {key: 'FBP;CGLS'}
        plugin.tools.set_plugin_list_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, ['FBP', 'CGLS'])
        self.assertEqual(plugin.get_plugin_tools().extra_dims[0], 2)

    def test_parameter_space_extra_dims(self):
        plugin = self.plugin_setup()
        key1 = 'algorithm'
        key2 = 'n_iterations'
        params = {key1: 'FBP;CGLS', key2: '1;2;3'}
        plugin.tools.set_plugin_list_parameters(params)
        out_datasets = plugin.get_out_datasets()
        for data in out_datasets:
            self.assertEqual(data.extra_dims, plugin.extra_dims)

    def test_parameter_space_data_shape(self):
        options = self.framework_options_setup()
        plugin = tu.plugin_runner_load_plugin(options)

        out_dataset = plugin.get_out_datasets()[0]
        self.assertEqual((160, 135, 160, 3, 2), out_dataset.get_shape())

#    def test_parameter_space_full_run(self):
#        options = self.framework_options_setup()
#        tu.plugin_runner_real_plugin_run(options)

if __name__ == "__main__":
    unittest.main()
