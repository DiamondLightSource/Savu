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
import copy
import copy_reg
import types
import pkgutil
import inspect
import imp

from savu.data.data_structures import utils as u

plugins = {}
plugins_path = {}
dawn_plugins = {}
dawn_plugin_params = {}
count = 0


def register_plugin(clazz):
    """decorator to add plugins to a central register"""
    plugins[clazz.__name__] = clazz
    if clazz.__module__.split('.')[0] != 'savu':
        plugins_path[clazz.__name__] = clazz.__module__
    return clazz


def dawn_compatible(clazz):
    """
    decorator to add dawn compatible plugins and details to a central register
    """
    dawn_plugins[clazz.__name__] = {}
    try:
        plugin_path = sys.modules[clazz.__module__].__file__
        dawn_plugins[clazz.__name__]['path2plugin'] = \
            plugin_path.split('.pyc')[0]+'.py'
    except Exception as e:
        print e
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
    try:
        mod = __import__(name)
    except ImportError:
        (path, name)=os.path.split(name)
        (name,ext) = os.path.splitext(name)
        (file, filename, data) = imp.find_module(name, [path])
        mod = imp.load_module(name, file, filename, data)
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


def set_datasets(exp, plugin, plugin_dict):
    in_names = get_names(plugin_dict["data"]["in_datasets"])
    out_names = get_names(plugin_dict["data"]["out_datasets"])

    default_in_names = plugin.parameters['in_datasets']
    default_out_names = plugin.parameters['out_datasets']

    in_names = in_names if in_names else default_in_names
    out_names = out_names if out_names else default_out_names

    in_names = ('all' if len(in_names) is 0 else in_names)
    out_names = (copy.copy(in_names) if len(out_names) is 0 else out_names)

    in_names = check_nDatasets(exp, in_names, plugin_dict,
                               plugin.nInput_datasets(), "in_data")
    out_names = check_nDatasets(exp, out_names, plugin_dict,
                                plugin.nOutput_datasets(), "out_data")

    for i in range(len(out_names)):
        new = out_names[i].split('in_datasets')
        if len(new) is 2:
            out_names[i] = in_names[int(list(new[1])[1])]

    plugin_dict["data"]["in_datasets"] = in_names
    plugin_dict["data"]["out_datasets"] = out_names

    plugin._set_parameters(plugin_dict['data'])
    plugin.base_dynamic_data_info()
    plugin.dynamic_data_info()


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

    mod_doc_lines = __get_doc_lines(sys.modules[dclass.__module__].__doc__)
    lines = __get_doc_lines(docstring)
    param_regexp = re.compile('^:param (?P<param>\w+):\s?(?P<doc>\w.*[^ ])\s' +
                              '?Default:\s?(?P<default>.*[^ ])$')
    param, idx1 = __find_regexp(param_regexp, lines)

    not_param_regexp = re.compile('^:~param (?P<param>\w+):')
    not_param, idx2 = __find_regexp(not_param_regexp, lines)

    warn_regexp = re.compile(r'^:config_warn: \s?(?P<config_warn>.*[^ ])$')
    warn, idx3 = __find_regexp(warn_regexp, lines)
    if not warn:
        warn = ['']
    syn_regexp = re.compile(r'^:synopsis: \s?(?P<synopsis>.*[^ ])$')
    synopsis, idx4 = __find_regexp(syn_regexp, mod_doc_lines)
    if not synopsis:
        synopsis = ['']

    info = __find_docstring_info(idx1+idx2+idx3+idx4, lines)

    param_entry = [{'dtype': type(value), 'name': a[0], 'desc': a[1],
                    'default': value} for a in param for value in [eval(a[2])]]

    return {'warn': "\n".join(warn), 'info': info, 'synopsis': synopsis[0],
            'param': param_entry, 'not_param': not_param}


def __get_doc_lines(doc):
    if not doc:
        return ['']
    return [" ".join(l.strip(' .').split()) for l in doc.split('\n')]


def __find_regexp(regexp, str_list):
    args = [regexp.findall(s) for s in str_list]
    index = [i for i in range(len(args)) if args[i]]
    args = [arg[0] for arg in args if len(arg)]
    return args, index


def __find_docstring_info(index, str_list):
    info = [str_list[i] for i in range(len(str_list)) if i not in index]
    info = [i for i in info if i]
    return "\n".join(info)


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


def set_pickles():
        copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)


def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


def populate_plugins():
    plugins_path = get_plugins_paths()
    savu_path = plugins_path[-1].split('savu')[0]
    savu_plugins = plugins_path[-1:]
    local_plugins = plugins_path[0:-1] + [savu_path + 'plugins_examples']

    # load local plugins
    for loader, module_name, is_pkg in pkgutil.walk_packages(local_plugins):
        _add_module(loader, module_name)

    # load savu plugins
    for loader, module_name, is_pkg in pkgutil.walk_packages(savu_plugins):
        if module_name.split('savu.plugins')[0] == '':
            _add_module(loader, module_name)

    for plugin in dawn_plugins.keys():
        p = load_plugin(dawn_plugins[plugin]['path2plugin'])
        dawn_plugins[plugin]['input rank'] = \
            u.get_pattern_rank(p.get_plugin_pattern())
        dawn_plugins[plugin]['description'] = p.__doc__.split(':param')[0]
        params = get_parameters(p)
        dawn_plugin_params[plugin] = params


def _add_module(loader, module_name):
    if module_name not in sys.modules:
        try:
            loader.find_module(module_name).load_module(module_name)
        except:
            pass


def get_parameters(plugin):
    params = {}
    for clazz in inspect.getmro(plugin.__class__):
        if clazz != object:
            args = find_args(clazz)
            for item in args['param']:
                if item['name'] not in ['in_datasets', 'out_datasets']:
                    params[item['name']] = {'value': item['default'],
                                            'hint': item['desc']}
    return params
