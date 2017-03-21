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
import atexit
import logging
import traceback
import pkgutil

from functools import wraps
import arg_parsers as parsers
import savu.plugins.utils as pu
import savu.data.data_structures.utils as du


if os.name == 'nt':
    import win_readline as readline
else:
    import readline

histfile = os.path.join(os.path.expanduser("~"), ".savuhist")
try:
    readline.read_history_file(histfile)
    readline.set_history_length(1000)
except IOError:
    pass
atexit.register(readline.write_history_file, histfile)

logging.basicConfig(level='CRITICAL')
error_level = 0


class DummyFile(object):
    def write(self, x): pass


def _redirect_stdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    return save_stdout


def _set_readline(completer):
    # we want to treat '/' as part of a word, so override the delimiters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)


def parse_args(function):
    @wraps(function)
    def _parse_args_wrap_function(content, args):
        doc = function.__doc__
        parser = '%s_arg_parser' % function.__name__
        args = getattr(parsers, parser)(args.split(), doc)
        if not args:
            return content
        return function(content, args)
    return _parse_args_wrap_function


def error_catcher(function):
    @wraps(function)
    def error_catcher_wrap_function(content, args):
        command = function.__name__.split('_')[1]
        try:
            return function(content, args)
        except Exception as e:
            savu_error = True if len(e.message.split()) > 1 and \
                e.message.split()[1] == 'ERROR:' else False
            if error_level is 0 and savu_error:
                print e.message
            if error_level is 0:
                print("Please type '%s -h' for help." % command)

            if error_level is 1:
                traceback.print_exc(file=sys.stdout)

            return content
    return error_catcher_wrap_function


def _add_module(loader, module_name):
    if module_name not in sys.modules:
        try:
            loader.find_module(module_name).load_module(module_name)
        except Exception:
            pass


def populate_plugins():
    # load all the plugins
    plugins_path = pu.get_plugins_paths()
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

    for plugin in pu.dawn_plugins.keys():
        p = pu.plugins[plugin]()
        pu.dawn_plugins[plugin]['input rank'] = \
            du.get_pattern_rank(p.get_plugin_pattern())
        pu.dawn_plugins[plugin]['description'] = p.__doc__.split(':param')[0]
        params = _get_dawn_parameters(p)
        pu.dawn_plugin_params[plugin] = params


def _get_dawn_parameters(plugin):
    plugin._populate_default_parameters()
    desc = plugin.parameters_desc
    params = {}
    for key, value in plugin.parameters.iteritems():
        if key not in ['in_datasets', 'out_datasets']:
            params[key] = {'value': value, 'hint': desc[key]}
    return params


def _populate_plugin_list(content, pfilter=""):
    """ Populate the plugin list from a list of plugin instances. """
    content.plugin_list.plugin_list = []
    sorted_plugins = __get_filtered_plugins(pfilter)
    count = 0
    for key in sorted_plugins:
        content.add(key, str(count))
        count += 1


def __get_filtered_plugins(pfilter):
    """ Get a sorted, filter list of plugins. """
    key_list = []
    star_search = \
        pfilter.split('*')[0] if pfilter and '*' in pfilter else False

    for key, value in pu.plugins.iteritems():
        if star_search:
            search = '(?i)^' + star_search
            if re.match(search, value.__name__) or \
                    re.match(search, value.__module__):
                key_list.append(key)
        elif pfilter in value.__module__ or pfilter in value.__name__:
            key_list.append(key)

    key_list.sort()
    return key_list


def __get_start_stop(content, start, stop):
    range_dict = {}
    if start:
        start = content.find_position(start)
        stop = content.find_position(stop) + 1 if stop else start + 1
        range_dict['start'] = start
        range_dict['stop'] = stop
    return range_dict
