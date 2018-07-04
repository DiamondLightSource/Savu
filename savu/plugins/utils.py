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
import re
import sys
import ast
import logging
import savu
import copy
import importlib
import imp
import inspect
from itertools import izip_longest


plugins = {}
plugins_path = {}
dawn_plugins = {}
dawn_plugin_params = {}
count = 0

OUTPUT_TYPE_DATA_ONLY = 0
OUTPUT_TYPE_METADATA_ONLY = 1
OUTPUT_TYPE_METADATA_AND_DATA = 2


def register_plugin(clazz):
    """decorator to add plugins to a central register"""
    plugins[clazz.__name__] = clazz
    if clazz.__module__.split('.')[0] != 'savu':
        plugins_path[clazz.__name__] = clazz.__module__
    return clazz


def dawn_compatible(plugin_output_type=OUTPUT_TYPE_METADATA_AND_DATA):
    def _dawn_compatible(clazz):
        """
        decorator to add dawn compatible plugins and details to a central
        register
        """
        dawn_plugins[clazz.__name__] = {}
        try:
            plugin_path = sys.modules[clazz.__module__].__file__
            # looks out for .pyc files
            dawn_plugins[clazz.__name__]['path2plugin'] = \
                plugin_path.split('.py')[0]+'.py'
            dawn_plugins[clazz.__name__]['plugin_output_type'] =\
                _plugin_output_type
        except Exception as e:
            print e
        return clazz
    # for backwards compatibility, if decorator is invoked without brackets...
    if inspect.isclass(plugin_output_type):
        _plugin_output_type = OUTPUT_TYPE_METADATA_AND_DATA
        return _dawn_compatible(plugin_output_type)
    else:
        _plugin_output_type = plugin_output_type
        return _dawn_compatible


def get_plugin(plugin_name):
    """ Get an instance of the plugin class and populate default parameters.

    :param plugin_name: Name of the plugin to import
    :type plugin_name: str.
    :returns:  An instance of the class described by the named plugin.
    """
    logging.debug("Importing the module %s", plugin_name)
    instance = load_class(plugin_name)()

    instance._populate_default_parameters()
    return instance


def load_class(name, cls_name=None):
    """ Returns an instance of the class associated with the module name.

    :param name: Module name or path to a module file
    :returns: An instance of the class associated with module.
    """
    path = name if os.path.dirname(name) else None
    name = os.path.basename(os.path.splitext(name)[0]) if path else name
    cls_name = ''.join(x.capitalize() for x in name.split('.')[-1].split('_'))\
        if not cls_name else cls_name
    if cls_name in plugins.keys():
        return plugins[cls_name]
    mod = \
        imp.load_source(name, path) if path else importlib.import_module(name)
    return getattr(mod, cls_name)


def plugin_loader(exp, plugin_dict, **kwargs):
    logging.debug("Running plugin loader")

    try:
        plugin = get_plugin(plugin_dict['id'])
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

    logging.debug("finished plugin loader")
    return plugin


def set_datasets(exp, plugin, plugin_dict):
    in_names = get_names(plugin_dict["data"], "in_datasets")
    out_names = get_names(plugin_dict["data"], "out_datasets")

    default_in_names = plugin.parameters['in_datasets']
    if 'out_datasets' in plugin.parameters.keys():
        default_out_names = plugin.parameters['out_datasets']
    else:
        default_out_names = []

    in_names = in_names if in_names else default_in_names
    out_names = out_names if out_names else default_out_names

    in_names = ('all' if len(in_names) is 0 else in_names)
    out_names = (copy.copy(in_names) if len(out_names) is 0 else out_names)

    in_names = check_nDatasets(
            exp, in_names, plugin_dict, plugin.nInput_datasets(), "in_data")

    clones = plugin.nClone_datasets()
    out_names = check_nDatasets(
            exp, out_names, plugin_dict, plugin.nOutput_datasets(),
            "out_data", clones=clones)

    if clones:
        out_names.extend(['itr_clone' + str(i) for i in range(clones)])

    for i in range(len(out_names)):
        new = out_names[i].split('in_datasets')
        if len(new) is 2:
            out_names[i] = in_names[int(list(new[1])[1])]

    plugin_dict["data"]["in_datasets"] = in_names
    plugin_dict["data"]["out_datasets"] = out_names

    plugin._set_parameters(plugin_dict['data'])
    plugin.base_dynamic_data_info()
    plugin.dynamic_data_info()


def get_names(pdict, key):
    try:
        data_names = pdict[key]
    except KeyError:
        data_names = []
    return data_names


def check_nDatasets(exp, names, plugin_dict, nSets, dtype, clones=0):
    plugin_id = plugin_dict['id']

    try:
        if names[0] in "all":
            names = exp._set_all_datasets(dtype)
    except IndexError:
        pass

    names = ([names] if type(names) is not list else names)
    if nSets is 'var':
        nSets = len(plugin_dict['data'][dtype + 'sets'])

    if len(names) is not (nSets - clones):
        if nSets is 0:
            names = []
        else:
            raise Exception("ERROR: Broken plugin chain. \n Please name the " +
                            str(nSets) + " " + dtype + " sets associated with "
                            " the plugin " + plugin_id + " in the process "
                            "file.")
    return names


def get_plugins_paths():
    """
    This gets the plugin paths, but also adds any that are not on the
    pythonpath to it.
    """
    plugins_paths = []
    user_plugin_path = os.path.join(os.path.expanduser("~"), 'savu_plugins')
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
    plugins_paths.append(os.path.join(savu.__path__[0]) + '/../')
    return plugins_paths


def is_template_param(param):
    """ Identifies if the parameter should be included in an input template
    and returns the default value of the parameter if it exists.
    """
    start = 0
    ptype = 'local'
    if isinstance(param, str):
        param = param.strip()
        if not param.split('global')[0]:
            ptype = 'global'
            start = 6
        first, last = param[start], param[-1]
        if first == '<' and last == '>':
            param = param[start+1:-1]
            try:
                exec("param = " + param)
            except:
                pass
            return [ptype, param]
    return False


def blockPrint():
    """ Disable printing to stdout """
    import tempfile
    fname = tempfile.mkdtemp() + '/unwanted_prints.txt'
    sys.stdout = open(fname, 'w')


def enablePrint():
    """ Enable printing to stdout """
    sys.stdout = sys.__stdout__


def parse_config_string(string):
    regex = "[\[\]\, ]+"
    split_vals = filter(None, re.split(regex, string))
    delimitors = re.findall(regex, string)
    split_vals = [repr(a.strip()) for a in split_vals]
    zipped = izip_longest(delimitors, split_vals)
    string = ''.join([i for l in zipped for i in l if i is not None])
    try:
        return ast.literal_eval(string)
    except ValueError:
        return ast.literal_eval(parse_array_index_as_string(string))


def parse_array_index_as_string(string):
    p = re.compile("'\['")
    for m in p.finditer(string):
        offset = m.start() - count + 3
        end = string[offset:].index("']") + offset
        string = string[:end] + "]'" + string[end+2:]
    string = string.replace("'['", '[')
    return string
