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
.. module:: utils
   :platform: Unix
   :synopsis: Utilities for plugin management

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import os
import sys
import re
import logging
import numpy as np
import savu

plugins = {}
plugins_path = {}
count = 0


def register_plugin(clazz):
    """decorator to add plugins to a central register"""
    plugins[clazz.__name__] = clazz
    if clazz.__module__.split('.')[0] != 'savu':
        plugins_path[clazz.__name__] = clazz.__module__
    return clazz


def load_plugin(plugin_name):
    """Load a plugin.

    :param plugin_name: Name of the plugin to import
                    path/loc/then.plugin.name if there is no path, then the
                    assumption is an internal plugin
    :type plugin_name: str.
    :returns:  An instance of the class described by the named plugin

    """
    logging.debug("getting class")
    logging.debug("plugin name is %s" % plugin_name)
    # clazz = self.import_class(plugin_name)

    name = plugin_name
    logging.debug("importing the module")
    if plugin_name.startswith(os.path.sep):
        # this is a path, so we need to add the directory to the pythonpath
        # and sort out the name
        ppath, name = os.path.split(plugin_name)
        sys.path.append(ppath)
    # TODO This appears to be the failing line.
    clazz = load_class(name)
    instance = get_class_instance(clazz)
    return instance


def get_class_instance(clazz):
    instance = clazz()
    instance._populate_default_parameters()
    return instance


def load_class(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    temp = name.split('.')[-1]
    mod2class = module2class(temp)
    clazz = getattr(mod, mod2class.split('.')[-1])
    return clazz


def module2class(module_name):
    return ''.join(x.capitalize() for x in module_name.split('_'))


def plugin_loader(exp, plugin_dict, **kwargs):
    logging.debug("Running plugin loader")

    try:
        plugin = load_plugin(plugin_dict['id'])
    except Exception as e:
        logging.error("failed to load the plugin")
        logging.error(e)
        raise e

    check_flag = kwargs.get('check', False)
    if check_flag:
        set_datasets(exp, plugin, plugin_dict)

    logging.debug("Running plugin main setup")
    plugin._main_setup(exp, plugin_dict['data'])

    if check_flag is True:
        exp.meta_data.plugin_list._set_datasets_list(plugin)

    logging.info("finished plugin loader")
    return plugin


def run_plugins(exp, plugin_list, **kwargs):
    n_loaders = exp.meta_data.plugin_list._get_n_loaders()

    for i in range(n_loaders):
        plugin_loader(exp, plugin_list[i])

    exp._barrier()
    exp._set_nxs_filename()
    exp._barrier()

    check = kwargs.get('check', False)
    for i in range(n_loaders, len(plugin_list)-1):
        exp._barrier()
        plugin_loader(exp, plugin_list[i], check=check)
        exp._merge_out_data_to_in()


def set_datasets(exp, plugin, plugin_dict):
    in_names = get_names(plugin_dict["data"]["in_datasets"])
    out_names = get_names(plugin_dict["data"]["out_datasets"])
    print plugin_dict["data"]
    print in_names, out_names

    default_in_names = plugin.parameters['in_datasets']
    default_out_names = plugin.parameters['out_datasets']

    in_names = in_names if in_names else default_in_names
    out_names = out_names if out_names else default_out_names

    in_names = ('all' if len(in_names) is 0 else in_names)
    out_names = (in_names if len(out_names) is 0 else out_names)

    in_names = check_nDatasets(exp, in_names, plugin_dict,
                               plugin.nInput_datasets(), "in_data")
    out_names = check_nDatasets(exp, out_names, plugin_dict,
                                plugin.nOutput_datasets(), "out_data")

    plugin_dict["data"]["in_datasets"] = in_names
    plugin_dict["data"]["out_datasets"] = out_names


def get_names(names):
    try:
        data_names = names
    except KeyError:
        data_names = []
    return data_names


def check_nDatasets(exp, names, plugin_dict, nSets, dtype):
    plugin_id = plugin_dict['id']
    try:
        if names[0] in "all":
            names = exp._set_all_datasets(dtype)
    except IndexError:
        pass

    errorMsg = "***ERROR: Broken plugin chain. \n Please name the " + \
        str(nSets) + " " + dtype + " sets associated with the plugin " + \
        plugin_id + " in the process file."

    names = ([names] if type(names) is not list else names)
    if nSets is 'var':
        nSets = len(plugin_dict['data'][dtype + 'sets'])

    if len(names) is not nSets:
        raise Exception(errorMsg)
    return names


def find_args(dclass, inst=None):
    """
    Finds the parameters list from the docstring
    """
    docstring = None
    if not dclass.__doc__:
        if inst:
            inst._override_class_docstring()
            docstring = dclass._override_class_docstring.__doc__
    else:
        docstring = dclass.__doc__

    if not docstring:
        return []

    lines = docstring.split('\n')
    param_regexp = re.compile('^:param (?P<param>\w+):\s?(?P<doc>\w.*[^ ])\s' +
                              '?Default:\s?(?P<default>.*[^ ])$')
    args = [param_regexp.findall(line.strip(' .')) for line in lines]
    args = [arg[0] for arg in args if len(arg)]
    return [{'dtype': type(value),
             'name': a[0], 'desc': a[1],
             'default': value} for a in args for value in [eval(a[2])]]


def calc_param_indices(dims):
    indices_list = []
    for i in range(len(dims)):
        chunk = int(np.prod(dims[0:i]))
        repeat = int(np.prod(dims[i+1:]))
        idx = np.ravel(np.kron(range(dims[i]), np.ones((repeat, chunk))))
        indices_list.append(idx.astype(int))
    return np.transpose(np.array(indices_list))


def get_plugins_paths():
    """
    This gets the plugin paths, but also adds any that are not 
    on the pythonpath to it.
    """
    plugins_paths = []
    user_plugin_path = os.path.join(os.path.expanduser("~"),'savu_plugins')
    if os.path.exists(user_plugin_path):
        plugins_paths.append(user_plugin_path)
    env_plugins_path = os.getenv("SAVU_PLUGINS_PATH")
    if env_plugins_path is not None:
        for ppath in (env_plugins_path.split(':')):
            if ppath != "":
                plugins_paths.append(ppath)
    # before we add the savu plugins to the list, add all items in the list
    # so far to the pythonpath
    for ppath in plugins_paths:
        if ppath not in sys.path:
            sys.path.append(ppath)
    # now add the savu plugin path, which is now the whole path.
    plugins_paths.append(os.path.join(savu.__path__[0], os.pardir))
    return plugins_paths