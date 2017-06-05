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
from savu.data.data_structures.plugin_data import PluginData
import savu.plugins.utils as pu


def get_test_data_path(name):
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] +
                    ['test_data/data', name])


def get_test_big_data_path(name):
    '''
    internal to diamond
    '''
    path = '/dls/mx-scratch/savu_test_data'
    return path+os.sep+name


def get_test_process_path(name):
    path = inspect.stack()[0][1]
    full_path = '/'.join(os.path.split(path)[0].split(os.sep)[:-2] +
                         ['test_data/test_process_lists', name])
    return full_path


def get_process_list_path(name):
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] +
                    ['test_data/process_lists', name])


def get_experiment_types():
    exp_dict = {}
    exp_dict['tomoRaw'] = {'func': 'set_tomoRaw_experiment',
                           'filename': '24737.nxs'}
    exp_dict['tomo'] = {'func': 'set_tomo_experiment',
                        'filename': 'savu_projections.h5'}
    exp_dict['fluo'] = {'func': 'set_fluo_experiment',
                        'filename': 'fluo.nxs'}
    exp_dict['tomo_3dto4d'] = {'func': 'set_3dto4d_experiment',
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
    options['loader'] = 'savu.plugins.loaders.full_field_loaders.nxtomo_loader'
    return options


def set_tomo_experiment(filename, **kwargs):
    options = set_options(get_test_data_path(filename), **kwargs)
    options['loader'] = 'savu.plugins.loaders.savu_loader'
    return options


def set_fluo_experiment(filename, **kwargs):
    options = set_options(get_test_data_path(filename), **kwargs)
    options['loader'] = 'savu.plugins.loaders.mapping_loaders.nxfluo_loader'
    return options


def set_3dto4d_experiment(filename, **kwargs):
    options = set_options(
        get_test_data_path('/i12_test_data/' + filename), **kwargs)
    options['loader'] = 'savu.plugins.loaders.full_field_loaders.nxtomo_loader'
    return options


def get_output_datasets(plugin):
    n_out = plugin.nOutput_datasets()
    out_data = []
    if n_out is 'var':
        return None
    for n in range(n_out):
        out_data.append('test' + str(n))
    return out_data


def set_plugin_list(options, pnames, *args):
    args = args[0] if args else None
    plugin_names = pnames if isinstance(pnames, list) else [pnames]
    options['plugin_list'] = []
    ID = [options['loader']]
    data = [{}, {}] if not args else [args[0], args[-1]]
    for i in range(len(plugin_names)):
        ID.insert(i+1, plugin_names[i])
        plugin = pu.get_plugin(plugin_names[i])
        data_dict = set_data_dict(['tomo'], get_output_datasets(plugin))
        data_dict = args[i+1] if args else data_dict
        data.insert(i+1, data_dict)

    for i in range(len(ID)):
        name = \
            ''.join(x.capitalize() for x in (ID[i].split('.')[-1]).split('_'))
        options['plugin_list'].append(set_plugin_entry(
            name, ID[i], data[i], i))


def set_plugin_entry(name, ID, data, pos):
    plugin = {}
    plugin['name'] = name
    plugin['id'] = ID
    plugin['data'] = data
    plugin['desc'] = data
    plugin['hide'] = []
    plugin['user'] = []
    plugin['active'] = []
    plugin['pos'] = str(pos)
    return plugin


def set_options(path, **kwargs):
    options = {}
    options['transport'] = kwargs.get('transport', 'hdf5')
    options['process_names'] = kwargs.get('process_names', 'CPU0')
    options['data_file'] = path
    options['process_file'] = kwargs.get('process_file', '')
    options['out_path'] = kwargs.get('out_path', tempfile.mkdtemp())
    options['out_folder'] = 'test'
    options['datafile_name'] = 'test'
    options['inter_path'] = options['out_path']
    options['log_path'] = options['out_path']
    options['run_type'] = 'test'
    options['verbose'] = 'True'
    options['link_type'] = 'final_result'
    options['test_state'] = True
    return options


def set_data_dict(in_data, out_data):
    return {'in_datasets': in_data, 'out_datasets': out_data}


def _add_loader_to_plugin_list(options, params={}):
    plugin_list = []
    ID = options['loader']
    name = ''.join(x.capitalize() for x in (ID.split('.')[-1]).split('_'))
    plugin_list.append(set_plugin_entry(name, ID, params, 0))
    options['plugin_list'] = plugin_list


def load_random_data(loader, params):
    options = set_options(get_test_data_path('24737.nxs'))
    options['loader'] = 'savu.plugins.loaders.' + str(loader)
    _add_loader_to_plugin_list(options, params=params)
    return plugin_runner(options)


def load_test_data(exp_type):
    options = set_experiment(exp_type)
    _add_loader_to_plugin_list(options)
    return plugin_runner(options)


def get_data_object(exp):
    data = exp.index['in_data'][exp.index['in_data'].keys()[0]]
    data._set_plugin_data(PluginData(data))
    pData = data._get_plugin_data()
    return data, pData


def set_process(exp, process, processes):
    exp.meta_data.set('process', process)
    exp.meta_data.set('processes', processes)


def plugin_runner(options):
    plugin_runner = PluginRunner(options)
    return plugin_runner._run_plugin_list()


def plugin_runner_load_plugin(options):
    plugin_runner = PluginRunner(options)
    plugin_runner.exp = Experiment(options)
    plugin_list = plugin_runner.exp.meta_data.plugin_list.plugin_list

    exp = plugin_runner.exp
    pu.plugin_loader(exp, plugin_list[0])
    exp._set_nxs_filename()

    plugin_dict = plugin_list[1]
    plugin = pu.get_plugin(plugin_dict['id'])
    plugin.exp = exp

    return plugin


def plugin_setup(plugin):
    plugin_list = plugin.exp.meta_data.plugin_list.plugin_list
    plugin_dict = plugin_list[1]
    pu.set_datasets(plugin.exp, plugin, plugin_dict)
    plugin._set_parameters(plugin_dict['data'])
    plugin._set_plugin_datasets()
    plugin.setup()


def plugin_runner_real_plugin_run(options):
    plugin_runner = PluginRunner(options)
    plugin_runner.exp = Experiment(options)
    plugin_list_inst = plugin_runner.exp.meta_data.plugin_list
    plugin_list = plugin_list_inst.plugin_list
    plugin_runner._run_plugin_list_check(plugin_list_inst)

    exp = plugin_runner.exp

    pu.plugin_loader(exp, plugin_list[0])

    start_in_data = copy.deepcopy(exp.index['in_data'])
    in_data = exp.index["in_data"][exp.index["in_data"].keys()[0]]
    out_data_objs, stop = in_data._load_data(1)
    exp._clear_data_objects()
    exp.index['in_data'] = copy.deepcopy(start_in_data)

    for key in out_data_objs[0]:
        exp.index["out_data"][key] = out_data_objs[0][key]

    plugin = pu.plugin_loader(exp, plugin_list[1])
    plugin._run_plugin(exp, plugin_runner)

#    out_datasets = plugin.parameters["out_datasets"]
#    exp._reorganise_datasets(out_datasets, 'final_result')
#
#    for key in exp.index["in_data"].keys():
#        exp.index["in_data"][key].close_file()


def get_test_process_list(folder):
    test_process_list = []
    for root, dirs, files in os.walk(folder, topdown=True):
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'nxs']
        for f in files:
            test_process_list.append(f)
    return test_process_list


def get_process_list(folder, search=False):
    process_list = []
    plugin_list = []
    exclude_dir = ['__pycache__']
    exclude_file = ['__init__.py']
    for root, dirs, files in os.walk(folder, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dir]
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
        files[:] = [fi for fi in files if fi not in exclude_file]
        processes = get_process_list_in_file(root, files)
        plugins = get_no_process_list_tests(root, files)
        for p in processes:
            process_list.append(p)
        for p in plugins:
            plugin_list.append(p)
    return process_list, plugin_list


def get_process_list_in_file(root, files):
    processes = []
    for fname in files:
        fname = root + '/' + fname
        in_file = open(fname, 'r')
        for line in in_file:
            if '.nxs' in line:
                processes.append(get_nxs_file_name(line))
    return processes


def get_no_process_list_tests(root, files):
    processes = []
    for fname in files:
        fname = root + '/' + fname
        in_file = open(fname, 'r')
        func = 'run_protected_plugin_runner_no_process_list'
        exclude = ['def', 'search_str']
        pos = 1
        param = get_param_name(func, pos, in_file, exclude=exclude)
        if param:
            in_file.seek(0)
            plugin_id_list = get_param_value_from_file(param, in_file)
            for pid in plugin_id_list:
                plugin_name = pid.split('.')[-1].split("'")[0]
                processes.append(plugin_name + '.py')
    return processes


def get_nxs_file_name(line):
    split_list = line.split("'")
    for entry in split_list:
        if 'nxs' in entry:
            if (len(entry.split(' ')) == 1):
                return entry


def get_param_name(func, pos, in_file, exclude=[]):
    """ Find the name of an argument passed to a function.

    :param str func: function name
    :param int pos: function argument position
    :param file in_file: open file to search
    :keyword list[str] exclude: ignore lines containing these strings.
                                Defaults to [].
    :returns: name associated with function argument
    :rtype: str
    """
    search_str = 'run_protected_plugin_runner_no_process_list('
    ignore = ['def', 'search_str']
    val_str = None
    for line in in_file:
        if search_str in line:
            if not [i in line for i in ignore].count(True):
                if ')' not in line:
                    line += next(in_file)
                params = line.split('(')[1].split(')')[0]
                val_str = params.split(',')[1].strip()
    return val_str


def get_param_value_from_file(param, in_file):
    """ Find all values associated with a parameter name in a file.

    :param str param: parameter name to search for
    :param file in_file: open file to search
    :returns: value associated with param
    :rtype: list[str]
    """
    param_list = []
    for line in in_file:
        if param in line and line.split('=')[0].strip() == param:
            if "\\" in line:
                line += next(in_file)
                line = ''.join(line.split('\\'))
            value = line.split('=')[1].strip()
            param_list.append(value)
    return param_list
