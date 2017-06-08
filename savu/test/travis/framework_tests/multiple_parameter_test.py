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
.. module:: multiple_parameter_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import unittest

import savu.plugins.utils as pu
import savu.test.test_utils as tu


class MultipleParameterTest(unittest.TestCase):

    def plugin_setup(self):
        ppath = 'savu.plugins.reconstructions.astra_recons.astra_recon_cpu'
        plugin = pu.get_plugin(ppath)
        return plugin

    def framework_options_setup(self):
        key1 = 'preview'
        key2 = 'FBP_filter'
        key3 = 'centre_of_rotation'
        key4 = 'in_datasets'
        key5 = 'out_datasets'
        key6 = 'force_zero'
        params = {key1: [':', '0', ':'], key2: 'ram-lak;hamming',
                  key3: '85.0;85.5;86.0', key4: 'tomo', key5: 'tomo',
                  key6: '[None, None]'}

        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.reconstructions.astra_recons.astra_recon_cpu'
        tu.set_plugin_list(options, plugin, [{}, params, {}])
        return options

    def test_parameter_space_int(self):
        plugin = self.plugin_setup()
        key = 'n_iterations'
        params = {'reconstruction_type': 'CGLS', 'preview': '[:,0,:]',
                  key: '1;2;3'}
        plugin._set_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, [1, 2, 3])
        self.assertEqual(plugin.extra_dims[0], 3)

    def test_parameter_space_float(self):
        plugin = self.plugin_setup()
        key = 'centre_of_rotation'
        params = {'preview': '[:,0,:]', key: '0.2;0.4;0.6'}
        plugin._set_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, [0.2, 0.4, 0.6])
        self.assertEqual(plugin.extra_dims[0], 3)

    def test_parameter_space_str(self):
        plugin = self.plugin_setup()
        key = 'FBP_filter'
        params = {'preview': '[:,0,:]', key: 'ram-lak;hamming'}
        plugin._set_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, ['ram-lak', 'hamming'])
        self.assertEqual(plugin.extra_dims[0], 2)

    def test_parameter_space_list(self):
        plugin = self.plugin_setup()
        key = 'force_zero'
        params = {'preview': '[:,0,:]', key: '[0, 1];[1, 2]'}
        plugin._set_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, [[0, 1], [1, 2]])
        self.assertEqual(plugin.extra_dims[0], 2)

    def test_parameter_space_extra_dims(self):
        plugin = self.plugin_setup()
        key1 = 'FBP_filter'
        key2 = 'centre_of_rotation'
        params = {key1: 'ram-lak;hamming', key2: '85.0;85.5;86.0'}
        plugin._set_parameters(params)
        out_datasets = plugin.get_out_datasets()
        for data in out_datasets:
            self.assertEqual(data.extra_dims, plugin.extra_dims)

    def test_parameter_space_data_shape(self):
        options = self.framework_options_setup()
        plugin = tu.plugin_runner_load_plugin(options)
        tu.plugin_setup(plugin)

        out_dataset = plugin.get_out_datasets()[0]
        self.assertEqual((160, 1, 160, 3, 2), out_dataset.get_shape())

#    def test_parameter_space_full_run(self):
#        options = self.framework_options_setup()
#        tu.plugin_runner_real_plugin_run(options)

if __name__ == "__main__":
    unittest.main()
