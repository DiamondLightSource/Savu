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

import sys
import os
import re

import numpy as np

plugins = {}


def register_plugin(clazz):
    """decorator to add logging information around calls for use with ."""
    plugins[clazz.__name__] = clazz
    return clazz


def load_plugin(plugin_name):
    """Load a plugin.

    :param plugin_name: Name of the plugin to import /path/loc/then.plugin.name
                    if there is no path, then the assumptiuon is an internal
                    plugin
    :type plugin_name: str.
    :returns:  An instance of the class described by the named plugin

    """
    # logging.debug("Running load_plugin")
    path, name = os.path.split(plugin_name)
    # logging.debug("Path is : %s", path)
    # logging.debug("Name is : %s", name)
    if (path is not '') and (path not in sys.path):
        # logging.debug("Appending path")
        sys.path.append(path)
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    clazz = getattr(mod, module2class(name.split('.')[-1]))
    instance = clazz()
    instance.populate_default_parameters()
    return instance


def module2class(module_name):
    """
    Converts a module name to a class name

    :param module_name: The lowercase_module_name of the module
    :type module_name: str
    :returns:  the module name in CamelCase
    """
    return ''.join(x.capitalize() for x in module_name.split('_'))

def find_args(dclass):
    """
    Finds the parameters list from the docstring
    """
    if not dclass.__doc__:
        return []
    lines = dclass.__doc__.split('\n')
    param_regexp = re.compile('^:param (?P<param>\w+):\s?(?P<doc>\w.*[^ ])\s' +
                              '?Default:\s?(?P<default>.*[^ ])$')
    args = [param_regexp.findall(line.strip(' .')) for line in lines]
    args = [arg[0] for arg in args if len(arg)]
    return [{'dtype': type(value),
             'name': a[0], 'desc': a[1],
             'default': value} for a in args for value in [eval(a[2])]]

