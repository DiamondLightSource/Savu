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
import importlib
import imp
import inspect
import itertools


load_tools = {}
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


def register_test_plugin(clazz):
    """decorator to add test plugins to a central register"""
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


def get_plugin(plugin_name, params, exp, check=False):
    """ Get an instance of the plugin class and populate default parameters.

    :param plugin_name: Name of the plugin to import
    :type plugin_name: str.
    :returns:  An instance of the class described by the named plugin.
    """
    logging.debug("Importing the module %s", plugin_name)
    instance = load_class(plugin_name)()
    instance.initialise(params, exp, check=check)
    return instance


def _get_cls_name(name):
    return ''.join(x.capitalize() for x in name.split('.')[-1].split('_'))


def load_class(name, cls_name=None):
    """ Returns an instance of the class associated with the module name.

    :param name: Module name or path to a module file
    :returns: An instance of the class associated with module.
    """
    path = name if os.path.dirname(name) else None
    name = os.path.basename(os.path.splitext(name)[0]) if path else name
    cls_name = _get_cls_name(name) if not cls_name else cls_name
    if cls_name in plugins.keys():
        return plugins[cls_name]
    mod = \
        imp.load_source(name, path) if path else importlib.import_module(name)
    return getattr(mod, cls_name)


def plugin_loader(exp, plugin_dict, check=False):
    logging.debug("Running plugin loader")
    try:
        plugin = get_plugin(
                plugin_dict['id'], plugin_dict['data'], exp, check=check)
    except Exception as e:
        logging.error("failed to load the plugin")
        logging.error(e)
        # re-raise the original error
        raise

    if check:
        exp.meta_data.plugin_list._set_datasets_list(plugin)

    logging.debug("finished plugin loader")
    return plugin

def get_tools_class(plugin_tools_id, cls=False):
    tool_class = None
    if plugin_tools_id == 'savu.plugins.plugin_tools':
        plugin_tools_id = 'savu.plugins.base_tools'

    # determine Savu base path
    path_name = plugin_tools_id.replace('.', '/')
    file_path =  savu.__path__[0] + '/../' + path_name + '.py'
    if os.path.isfile(file_path):
        if cls:
            tool_class = load_class(plugin_tools_id)(cls)
        else:
            tool_class = load_class(plugin_tools_id)

    return tool_class


def get_plugins_paths(examples=True):
    """
    This gets the plugin paths, but also adds any that are not on the
    pythonpath to it.
    """
    plugins_paths = []
    # get user and environment plugin paths
    user_path = [os.path.join(os.path.expanduser("~"), 'savu_plugins')]
    env_paths = list(itertools.ifilter(None, (
            os.getenv("SAVU_PLUGINS_PATH") or "").replace(" ","").split(":")))
    
    # If examples have been requested then add them to the path
    # add all sub folders
    eg_base_path = os.path.join(savu.__path__[0],
                           "../plugin_examples/plugin_templates")
    eg_path = [x[0] for x in os.walk(eg_base_path)] if examples else []
    # check all paths exist and add the the plugin paths
    for ppath in user_path + env_paths + eg_path:
        if os.path.exists(ppath):
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
            param = None if not param else param
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
    zipped = itertools.izip_longest(delimitors, split_vals)
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


def param_to_str(param_name, keys):
    """ Check the parameter is within the provided list and
    return the string name.
    """
    if param_name.isdigit():
        param_name = int(param_name)
        if param_name <= len(keys):
            param_name = keys[param_name-1]
        else:
            raise Exception('This parameter number is not valid for this plugin')
    elif param_name not in keys:
        raise Exception('This parameter is not present in this plug in.')

    return param_name


def set_order_by_visibility(parameters, level=False):
    """ Return an ordered list of parameters depending on the
    visibility level

    :param parameters: The dictionary of parameters
    :param level: The visibility level
    :return: An ordered list of parameters
    """
    data_keys = []
    basic_keys = []
    interm_keys = []
    adv_keys = []
    for k, v in parameters.items():
        if v['display'] == 'on':
            if v['visibility'] == 'datasets':
                data_keys.append(k)
            if v['visibility'] == 'basic':
                basic_keys.append(k)
            if v['visibility'] == 'intermediate':
                interm_keys.append(k)
            if v['visibility'] == 'advanced':
                adv_keys.append(k)
    if level:
        if level == 'datasets':
            keys = data_keys
        elif level == 'basic':
            keys = basic_keys
        elif level == 'intermediate':
            keys = basic_keys + interm_keys + data_keys
        elif level == 'advanced':
            keys = basic_keys + interm_keys + adv_keys + data_keys
        else:
            keys = basic_keys + interm_keys + adv_keys + data_keys
    else:
        keys =  basic_keys + interm_keys + adv_keys + data_keys

    return keys