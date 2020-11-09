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
import inspect
import itertools

from collections import OrderedDict

# can I remove these from here?
plugins = {}
plugins_path = {}
dawn_plugins = {}
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
            dawn_plugins[clazz.__name__]['path2plugin'] = plugin_path.split('.py')[0] + '.py'
            dawn_plugins[clazz.__name__]['plugin_output_type'] = _plugin_output_type
        except Exception as e:
            print(e)
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
    if path:
        mod = importlib.machinery.SourceFileLoader(name, path).load_module()
    else:
        mod = importlib.import_module(name)
    return getattr(mod, cls_name)


def plugin_loader(exp, plugin_dict, check=False):
    logging.debug("Running plugin loader")
    try:
        plugin = get_plugin(plugin_dict['id'],
                            plugin_dict['data'],
                            exp,
                            check=check)
    except Exception as e:
        logging.error("failed to load the plugin")
        logging.error(e)
        # re-raise the original error
        raise

    if check:
        exp.meta_data.plugin_list._set_datasets_list(plugin)

    logging.debug("finished plugin loader")
    return plugin


def get_plugins_paths(examples=True):
    """
    This gets the plugin paths, but also adds any that are not on the
    pythonpath to it.
    """
    plugins_paths = OrderedDict()
    
    # Add the savu plugins paths first so it is overridden by user folders
    savu_plugins_path = os.path.join(savu.__path__[0], 'plugins')
    savu_plugins_subpaths = [d for d in next(os.walk(savu_plugins_path))[1] \
                             if d != "__pycache__"]
    for path in savu_plugins_subpaths:
        plugins_paths[os.path.join(savu_plugins_path, path)] = \
            ''.join(['savu.plugins.', path, '.'])
    
    # get user, environment and example plugin paths
    user_path = [os.path.join(os.path.expanduser("~"), 'savu_plugins')]
    env_paths = os.getenv("SAVU_PLUGINS_PATH", "").replace(" ", "").split(":")
    templates = "../plugin_examples/plugin_templates"
    eg_path = [os.path.join(savu.__path__[0], templates)] if examples else []

    for ppath in env_paths + user_path + eg_path:
        if os.path.exists(ppath):
            plugins_paths[ppath] = os.path.basename(ppath) + '.'
            if ppath not in sys.path:
                sys.path.append(os.path.dirname(ppath))

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
            param = param[start + 1:-1]
            param = None if not param else param
            try:
                param = eval(param)
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
    regex = r"[\[\]\, ]+"
    split_vals = [_f for _f in re.split(regex, string) if _f]
    delimitors = re.findall(regex, string)
    split_vals = [repr(a.strip()) for a in split_vals]
    zipped = itertools.zip_longest(delimitors, split_vals)
    string = ''.join([i for l in zipped for i in l if i is not None])
    try:
        return ast.literal_eval(string)
    except ValueError:
        return ast.literal_eval(parse_array_index_as_string(string))


def parse_array_index_as_string(string):
    p = re.compile(r"'\['")
    for m in p.finditer(string):
        offset = m.start() - count + 3
        end = string[offset:].index("']") + offset
        string = string[:end] + "]'" + string[end + 2:]
    string = string.replace("'['", '[')
    return string
