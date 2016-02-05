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
.. module:: test_utils
   :platform: Unix
   :synopsis: utilities for the test framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import inspect
import tempfile
import os
import copy

from savu.core.plugin_runner import PluginRunner
from savu.data.experiment_collection import Experiment
import savu.plugins.utils as pu
from savu.data.data_structures import PluginData


def get_test_data_path(name):
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] +
                    ['test_data/data', name])


def get_test_process_path(name):
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] +
                    ['test_data/test_process_lists', name])


def get_process_list_path(name):
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] +
                    ['test_data/process_lists', name])


def get_experiment_types():
    exp_dict = {}
    exp_dict['tomoRaw'] = {'func': 'set_tomoRaw_experiment',
                           'filename': '24737.nxs'}
    exp_dict['tomo'] = {'func': 'set_tomo_experiment',
                        'filename': 'projections.h5'}
    exp_dict['fluo'] = {'func': 'set_fluo_experiment',
                        'filename': 'fluo.nxs'}
    exp_dict['i12tomo'] = {'func': 'set_i12tomo_experiment',
                           'filename': 'i12_test_data.nxs'}

    return exp_dict


def set_experiment(exp_type, **kwargs):
    exp_types = get_experiment_types()
    try:
        options = globals()[exp_types[exp_type]['func']](
            exp_types[exp_type]['filename'], **kwargs)
    except KeyError:
        raise Exception("The experiment type ", exp_type, " is not recognised")
    return options


def set_tomoRaw_experiment(filename, **kwargs):
    # create experiment
    options = set_options(get_test_data_path(filename))
    options['loader'] = 'savu.plugins.loaders.nxtomo_loader'
    options['saver'] = 'savu.plugins.savers.hdf5_tomo_saver'
    return options


def set_tomo_experiment(filename, **kwargs):
    options = set_options(get_test_data_path(filename), **kwargs)
    options['loader'] = 'savu.plugins.loaders.projection_tomo_loader'
    options['saver'] = 'savu.plugins.savers.hdf5_tomo_saver'
    return options


def set_fluo_experiment(filename, **kwargs):
    options = set_options(get_test_data_path(filename), **kwargs)
    options['loader'] = 'savu.plugins.loaders.nxfluo_loader'
    options['saver'] = 'savu.plugins.savers.hdf5_tomo_saver'
    return options


def set_i12tomo_experiment(filename, **kwargs):
    options = \
        set_options(get_test_data_path('/i12_test_data/' + filename), **kwargs)
    options['loader'] = 'savu.plugins.loaders.i12_tomo_loader'
    options['saver'] = 'savu.plugins.savers.hdf5_tomo_saver'
    return options


def get_output_datasets(plugin):
    n_out = plugin.nOutput_datasets()
    out_data = []
    for n in range(n_out):
        out_data.append('test' + str(n))
    return out_data


def set_plugin_list(options, pnames, *args):
    args = args[0] if args else None
    plugin_names = pnames if isinstance(pnames, list) else [pnames]
    options['plugin_list'] = []
    ID = [options['loader'], options['saver']]
    data = [{}, {}] if not args else [args[0], args[-1]]
    for i in range(len(plugin_names)):
        ID.insert(i+1, plugin_names[i])
        plugin = pu.load_plugin(plugin_names[i])
        data_dict = set_data_dict(['tomo'], get_output_datasets(plugin))
        data_dict = args[i+1] if args else data_dict
        data.insert(i+1, data_dict)

    for i in range(len(ID)):
        name = pu.module2class(ID[i].split('.')[-1])
        options['plugin_list'].append(set_plugin_entry(name, ID[i], data[i]))


def set_plugin_entry(name, ID, data):
    plugin = {}
    plugin['name'] = name
    plugin['id'] = ID
    plugin['data'] = data
    return plugin


def set_options(path, **kwargs):
    process_file = kwargs.get('process_file', '')
    process_names = kwargs.get('process_names', 'CPU0')
    options = {}
    options['transport'] = 'hdf5'
    options['process_names'] = process_names
    options['data_file'] = path
    options['process_file'] = process_file
    options['out_path'] = tempfile.mkdtemp()
    options['run_type'] = 'test'
    return options


def set_data_dict(in_data, out_data):
    return {'in_datasets': in_data, 'out_datasets': out_data}


def load_test_data(exp_type):
    options = set_experiment(exp_type)

    plugin_list = []
    ID = options['loader']
    name = pu.module2class(ID.split('.')[-1])
    plugin_list.append(set_plugin_entry(name, ID, {}))
    ID = options['saver']
    name = pu.module2class(ID.split('.')[-1])
    plugin_list.append(set_plugin_entry(name, ID, {}))

    # currently assuming an empty parameters dictionary
    options['plugin_list'] = plugin_list
    return plugin_runner(options)


def get_data_object(exp):
    data = exp.index['in_data'][exp.index['in_data'].keys()[0]]
    data.set_plugin_data(PluginData(data))
    pData = data.get_plugin_data()
    return data, pData


def set_process(exp, process, processes):
    exp.meta_data.set_meta_data('process', process)
    exp.meta_data.set_meta_data('processes', processes)


def plugin_runner(options):
    plugin_runner = PluginRunner(options)
    return plugin_runner.run_plugin_list(options)


def plugin_runner_load_plugin(options):
    plugin_runner = PluginRunner(options)
    plugin_runner.exp = Experiment(options)
    plugin_list = plugin_runner.exp.meta_data.plugin_list.plugin_list

    exp = plugin_runner.exp
    pu.plugin_loader(exp, plugin_list[0])
    exp.set_nxs_filename()

    plugin_dict = plugin_list[1]
    plugin = pu.load_plugin(plugin_dict['id'])
    plugin.exp = exp

    return plugin


def plugin_setup(plugin):
    plugin_list = plugin.exp.meta_data.plugin_list.plugin_list
    plugin_dict = plugin_list[1]
    pu.set_datasets(plugin.exp, plugin, plugin_dict)
    plugin.set_parameters(plugin_dict['data'])
    plugin.set_plugin_datasets()
    plugin.setup()


def plugin_runner_real_plugin_run(options):
    plugin_runner = PluginRunner(options)
    plugin_runner.exp = Experiment(options)
    plugin_list = plugin_runner.exp.meta_data.plugin_list.plugin_list
    plugin_runner.run_plugin_list_check(plugin_list)

    exp = plugin_runner.exp

    pu.plugin_loader(exp, plugin_list[0])

    start_in_data = copy.deepcopy(exp.index['in_data'])
    in_data = exp.index["in_data"][exp.index["in_data"].keys()[0]]
    out_data_objs, stop = in_data.load_data(1)
    exp.clear_data_objects()
    exp.index['in_data'] = copy.deepcopy(start_in_data)

    for key in out_data_objs[0]:
        exp.index["out_data"][key] = out_data_objs[0][key]

    plugin = pu.plugin_loader(exp, plugin_list[1])
    plugin.run_plugin(exp, plugin_runner)

#    out_datasets = plugin.parameters["out_datasets"]
#    exp.reorganise_datasets(out_datasets, 'final_result')
#
#    for key in exp.index["in_data"].keys():
#        exp.index["in_data"][key].close_file()
