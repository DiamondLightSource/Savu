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
import glob
import shutil

from savu.core.plugin_runner import PluginRunner
from savu.data.experiment_collection import Experiment
from savu.data.data_structures.plugin_data import PluginData
import savu.plugins.utils as pu
import savu.test.base_checkpoint_test


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
                           'filename': 'tomo_standard.nxs'}
    exp_dict['tomo'] = {'func': 'set_tomo_experiment',
                        'filename': '24737_processed.nxs'}
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
    options = set_options(get_test_data_path('/full_field_corrected/' + filename), **kwargs)
    options['loader'] = 'savu.plugins.loaders.savu_nexus_loader'
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
    if n_out == 'var':
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
        plugin = pu.load_class(plugin_names[i])()
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
    options['nProcesses'] = len(options["process_names"].split(','))
    options['data_file'] = path
    options['process_file'] = kwargs.get('process_file', '')
    options['out_path'] = kwargs.get('out_path', tempfile.mkdtemp())
    options['out_folder'] = 'test'
    options['datafile_name'] = 'test'
    options['inter_path'] = options['out_path']
    options['log_path'] = options['out_path']
    options['run_type'] = 'test'
    options['verbose'] = 'True'
    #options['link_type'] = 'final_result'
    options['test_state'] = True
    options['lustre'] = False
    options['bllog'] = None
    options['email'] = None
    options['template'] = None
    options['checkpoint'] = None
    options['system_params'] = None
    options['nPlugin'] = 0
    options['command'] = ''
    options['pre_run'] = False
    options['post_pre_run'] = False
    options['stats'] = "on"
    return options


def set_data_dict(in_data, out_data):
    return {'in_datasets': in_data, 'out_datasets': out_data}


def _add_loader_to_plugin_list(options, params={}):
    plugin_list = []
    ID = options['loader']
    name = ''.join(x.capitalize() for x in (ID.split('.')[-1]).split('_'))
    plugin_list.append(set_plugin_entry(name, ID, params, 0))
    options['plugin_list'] = plugin_list


def load_random_data(loader, params, system_params=None, fake=False):
    options = set_options(get_test_data_path('tomo_standard.nxs'))
    options['loader'] = 'savu.plugins.loaders.' + str(loader)
    options['system_params'] = system_params
    _add_loader_to_plugin_list(options, params=params)
    if fake:
        return fake_plugin_runner(options).exp
    return plugin_runner(options)


def load_test_data(exp_type):
    options = set_experiment(exp_type)
    _add_loader_to_plugin_list(options)
    return plugin_runner(options)


def get_data_object(exp):
    data = exp.index['in_data'][list(exp.index['in_data'].keys())[0]]
    data._set_plugin_data(PluginData(data))
    pData = data._get_plugin_data()
    return data, pData


def set_process(exp, process, processes):
    exp.meta_data.set('process', process)
    exp.meta_data.set('processes', processes)


def plugin_runner(options):
    # the real plugin runner runs a full plugin list
    plugin_runner = PluginRunner(options)
    return plugin_runner._run_plugin_list()


def fake_plugin_runner(options):
    # Stripped down version of the plugin runner
    # Loads the loader plugin but stops before processing plugins
    plugin_runner = PluginRunner(options)
    plugin_runner.exp = Experiment(options)
    plugin_list = plugin_runner.exp.meta_data.plugin_list.plugin_list

    exp = plugin_runner.exp
    pu.plugin_loader(exp, plugin_list[0])
    exp._set_nxs_file()
    return plugin_runner


def plugin_runner_load_plugin(options):
    # Loads the loader plugin and the first plugin in the list and initialises
    # it (i.e. sets parameters and calls setup method)
    pRunner = fake_plugin_runner(options)
    plugin_list = pRunner.exp.meta_data.plugin_list.plugin_list
    plugin_dict = plugin_list[1]
    plugin = pu.plugin_loader(pRunner.exp, plugin_dict)
    return plugin


def plugin_runner_real_plugin_run(options):
    plugin_runner = PluginRunner(options)
    plugin_list_inst = plugin_runner.exp.meta_data.plugin_list
    plugin_list = plugin_list_inst.plugin_list
    plugin_runner._run_plugin_list_check(plugin_list_inst)

    exp = plugin_runner.exp
    pu.plugin_loader(exp, plugin_list[0])

    start_in_data = copy.deepcopy(exp.index['in_data'])
    in_data = exp.index["in_data"][list(exp.index["in_data"].keys())[0]]
    out_data_objs, stop = in_data._load_data(1)
    exp._clear_data_objects()
    exp.index['in_data'] = copy.deepcopy(start_in_data)

    for key in out_data_objs[0]:
        exp.index["out_data"][key] = out_data_objs[0][key]

    plugin = pu.plugin_loader(exp, plugin_list[1])
    plugin._run_plugin(exp, plugin_runner)


def initialise_options(data, experiment, process_path):
    """
    initialises options and creates a temporal directory in tmp for output.

    :param str data: data to run test with (can be None)
    :param str experiment: experiment type to run test with (can be None)
    :param str process_path: a path to the preocess list (can be None)
    """
    test_folder = tempfile.mkdtemp(suffix='my_test/')
    if data is not None:
        data_file = get_test_data_path(data)
    if process_path is not None:
        process_file = get_test_process_path(process_path)
    if (experiment is not None) & (data is None):
        options = set_experiment(experiment)
    elif (experiment is not None) & (data is not None):
        if experiment == 'load_data':
            options = set_experiment('tomo')
            options['data_file'] = data
        else:
            options = set_experiment(experiment)
            options['data_file'] = data_file
        options['process_file'] = process_file
    else:
        options = set_options(data_file, process_file=process_file)
    options['out_path'] = os.path.join(test_folder)
    return options


def cleanup(options):
    """
    Performs folders cleaning in tmp/.
    using _shutil_ module in order to delete everything recursively
    """
    shutil.rmtree(options["out_path"], ignore_errors=True)
    """
    classb = savu.test.base_checkpoint_test.BaseCheckpointTest()
    cp_folder = os.path.join(options["out_path"], 'checkpoint')
    classb._empty_folder(cp_folder)
    # delete folders after imagesavers
    im_folder = os.path.join(options["out_path"], 'ImageSaver-tomo')
    if os.path.isdir(im_folder):
        classb._empty_folder(im_folder)
        os.removedirs(im_folder)
    im_folder = os.path.join(options["out_path"], 'TiffSaver-tomo')
    if os.path.isdir(im_folder):
        classb._empty_folder(im_folder)
        os.removedirs(im_folder)
    os.removedirs(cp_folder)
    classb._empty_folder(options["out_path"])
    os.removedirs(options["out_path"])
    """
    return options
