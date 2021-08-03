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
.. module:: config_utils
   :platform: Unix
   :synopsis: Helper functions for the configurator commands.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import re
import sys
import os
import mmap
import atexit
import logging
import traceback
import pkgutil

import importlib.util
from functools import wraps
import savu.plugins.utils as pu
import savu.data.data_structures.utils as du

if os.name == "nt":
    from . import win_readline as readline
else:
    import readline

histfile = os.path.join(os.path.expanduser("~"), ".savuhist")
histlen = 1000
logging.basicConfig(level="CRITICAL")
error_level = 0


class DummyFile(object):
    def write(self, x):
        pass


def _redirect_stdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    return save_stdout


def load_history_file(hfile):
    try:
        readline.read_history_file(hfile)
        readline.set_history_length(histlen)
    except IOError:
        pass
    atexit.register(write_history_to_file)


def write_history_to_file():
    try:
        readline.write_history_file(histfile)
    except IOError:
        pass


def _set_readline(completer):
    # we want to treat '/' as part of a word, so override the delimiters
    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)


def parse_args(function):
    @wraps(function)
    def _parse_args_wrap_function(content, args):
        parser = "%s_arg_parser" % function.__name__
        from . import arg_parsers as parsers

        args = getattr(parsers, parser)(args.split(), doc=False)
        if not args:
            return content
        return function(content, args)

    return _parse_args_wrap_function


def error_catcher(function):
    @wraps(function)
    def error_catcher_wrap_function(content, args):
        try:
            return function(content, args)
        except Exception as e:
            err_msg_list = str(e).split()
            savu_error = True if len(err_msg_list) > 1 and err_msg_list[1] == 'ERROR:' else False

            if error_level == 0 and savu_error:
                print(e)
            elif error_level == 0:
                print(f"{type(e).__name__}: {e}")
            elif error_level == 1:
                traceback.print_exc(file=sys.stdout)

            return content

    return error_catcher_wrap_function


def populate_plugins(error_mode=False, examples=False):
    # load all the plugins
    plugins_paths = pu.get_plugins_paths(examples=examples)
    failed_imports = {}

    for path, name in plugins_paths.items():
        for finder, module_name, is_pkg in pkgutil.walk_packages([path], name):
            if not is_pkg:
                failed_imports = _load_module(finder, module_name, failed_imports, error_mode)
    return failed_imports


def _load_module(finder, module_name, failed_imports, error_mode):
    try:
        # need to ignore loading of plugin.utils as it is emptying the list
        spec = finder.find_spec(module_name)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        # Load the plugin class and ensure the tools file is present
        plugin = pu.load_class(module_name)()
        if not plugin.get_plugin_tools():
            raise Exception(f"Tools file not found.")
    except Exception as e:
        if _is_registered_plugin(mod):
            clazz = pu._get_cls_name(module_name)
            failed_imports[clazz] = e
            if error_mode:
                print(("\nUnable to load plugin %s\n%s" % (module_name, e)))
    return failed_imports


def _is_registered_plugin(mod):
    with open(mod.__file__) as f:
        for line in f:
            if "@register_plugin" in line and line.replace(" ", "")[0] != "#":
                return True
    return False


def _dawn_setup():
    for plugin in list(pu.dawn_plugins.keys()):
        p = pu.plugins[plugin]()
        pu.dawn_plugins[plugin]['input rank'] = \
            du.get_pattern_rank(p.get_plugin_pattern())
        pu.dawn_plugins[plugin]['description'] = p.__doc__.split(':param')[0]
        params = _get_dawn_parameters(p)
        pu.dawn_plugin_params[plugin] = params


def _get_dawn_parameters(plugin):
    plugin.get_plugin_tools()._populate_default_parameters()
    desc = plugin.p_dict["description"]
    params = {}
    for key, value in plugin.parameters.items():
        if key not in ["in_datasets", "out_datasets"]:
            params[key] = {"value": value, "hint": desc[key]}
    return params


def _populate_plugin_list(content, pfilter=""):
    """ Populate the plugin list from a list of plugin instances. """
    content.plugin_list.plugin_list = []
    sorted_plugins = __get_filtered_plugins(pfilter)
    count = 0
    for key in sorted_plugins:
        content.add(key, str(count))
        count += 1


def _search_plugin_file(module_name, pfilter):
    """Check for string inside file"""
    string_found = False

    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('scripts')[0]
    file_dir = module_name.replace('.', '/')
    file_path = savu_base_path + file_dir + '.py'
    if os.path.isfile(file_path):
        plugin_file = open(file_path, "r")
        data = plugin_file.read().split()
        if pfilter in data:
            string_found = True
        plugin_file.close()
    return string_found


def __get_filtered_plugins(pfilter):
    """ Get a sorted, filter list of plugins. """
    key_list = []
    star_search = \
        pfilter.split("*")[0] if pfilter and "*" in pfilter else False

    for key, value in pu.plugins.items():
        if star_search:
            search = '(?i)^' + star_search
            if re.match(search, value.__name__) or \
                    re.match(search, value.__module__):
                key_list.append(key)
        elif pfilter in value.__module__ or pfilter in value.__name__:
            key_list.append(key)
        else:
            # Check if the word is present in the file
            if _search_plugin_file(value.__module__, pfilter):
                key_list.append(key)

    key_list.sort()
    return key_list
