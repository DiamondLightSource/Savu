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
import os

def get_test_data_path(name):
    path = inspect.stack()[0][1]
    return '/'.join(os.path.split(path)[0].split(os.sep)[:-2] +
                    ['test_data', name])

def get_experiment_types():
    exp_dict = {}
    exp_dict['tomoRaw'] = {'func': 'set_tomoRaw_experiment', 'filename': '24737.nxs'}
    exp_dict['tomo'] = {'func': 'set_tomo_experiment', 'filename': 'projections.h5'}
    return exp_dict

def set_experiment(exp_type):
    exp_types = get_experiment_types()
    try:
        options = globals()[exp_types[exp_type]['func']] \
                                            (exp_types[exp_type]['filename'])
    except KeyError:
        raise Exception("The experiment type ", exp_type, " is not recognised")
    return options

def set_tomoRaw_experiment(filename):
    # create experiment
    options = set_options(get_test_data_path(filename))
    options['loader'] = 'savu.plugins.nxtomo_loader'
    options['saver'] = 'savu.plugins.hdf5_tomo_saver'
    options['plugin_datasets'] = set_data_dict(['tomo'], ['tomo'])
    return options

def set_tomo_experiment(filename):
    # create experiment
    options = set_options(get_test_data_path(filename))
    options['loader'] = 'savu.plugins.projection_tomo_loader'
    options['saver'] = 'savu.plugins.hdf5_tomo_saver'
    options['plugin_datasets'] = set_data_dict(['tomo'], ['tomo'])
    return options

def set_plugin_list(options, plugin_name):
    options['plugin_list'] = []
    ID = [options['loader'], plugin_name, options['saver']]
    data = [{}, options['plugin_datasets'], {}]
    for i in range(len(ID)):
        name = module2class(ID[i].split('.')[-1])
        options['plugin_list'].append(set_plugin_entry(name, ID[i], data[i]))

def set_plugin_entry(name, ID, data):
    plugin = {}
    plugin['name'] = name
    plugin['id'] = ID
    plugin['data'] = data
    return plugin 

def set_options(path):
    options = {}
    options['transport'] = 'hdf5'
    options['process_names'] = 'CPU0'
    options['data_file'] = path
    options['process_file'] = ''
    options['out_path'] = '/tmp'
    options['run_type'] = 'test'
    return options
    
def set_data_dict(in_data, out_data):
    return {'in_datasets': in_data, 'out_datasets': out_data}

def get_class_instance(clazz):
    instance = clazz()
    return instance

def module2class(module_name):
    return ''.join(x.capitalize() for x in module_name.split('_'))

def load_class(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    temp = name.split('.')[-1]
    mod2class = module2class(temp)
    clazz = getattr(mod, mod2class.split('.')[-1])
    instance = get_class_instance(clazz)
    return instance



