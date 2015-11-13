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

import re
import logging

plugins = {}


def register_plugin(clazz):
    """decorator to add logging information around calls for use with ."""
    plugins[clazz.__name__] = clazz
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
    # TODO This appears to be the failing line.
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    temp = name.split('.')[-1]
    mod2class = module2class(temp)
    clazz = getattr(mod, mod2class.split('.')[-1])
    instance = get_class_instance(clazz)
    return instance


def get_class_instance(clazz):
    instance = clazz()
    instance.populate_default_parameters()
    return instance


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
    plugin.main_setup(exp, plugin_dict['data'])

    logging.debug("finished plugin loader")
    return plugin


def run_plugins(exp, plugin_list, **kwargs):
    plugin_loader(exp, plugin_list[0])
    exp.set_nxs_filename()

    check = kwargs.get('check', False)
    for i in range(1, len(plugin_list)-1):
        exp.barrier()
        logging.info("Checking Plugin %s" % plugin_list[i]['name'])
        plugin_loader(exp, plugin_list[i], check=check)
        exp.merge_out_data_to_in()


def set_datasets(exp, plugin, plugin_dict):
    in_names = get_names(plugin_dict["data"]["in_datasets"])
    out_names = get_names(plugin_dict["data"]["out_datasets"])

    default_in_names = plugin.parameters['in_datasets']
    default_out_names = plugin.parameters['out_datasets']

    in_names = in_names if in_names else default_in_names
    out_names = out_names if out_names else default_out_names

    in_names = ('all' if len(in_names) is 0 else in_names)
    out_names = (in_names if len(out_names) is 0 else out_names)

    in_names = check_nDatasets(exp, in_names, plugin_dict["id"],
                               plugin.nInput_datasets(), "in_data")
    out_names = check_nDatasets(exp, out_names, plugin_dict["id"],
                                plugin.nOutput_datasets(), "out_data")

    plugin_dict["data"]["in_datasets"] = in_names
    plugin_dict["data"]["out_datasets"] = out_names


def get_names(names):
    try:
        data_names = names
    except KeyError:
        data_names = []
    return data_names


def check_nDatasets(exp, names, plugin_id, nSets, dtype):
    print names, plugin_id
    try:
        if names[0] in "all":
            names = exp.set_all_datasets(dtype)
    except IndexError:
        pass

    errorMsg = "***ERROR: Broken plugin chain. \n Please name the " + \
        str(nSets) + " " + dtype + " sets associated with the plugin " + \
        plugin_id + " in the process file."

    names = ([names] if type(names) is not list else names)
    if len(names) is not nSets:
        raise Exception(errorMsg)
    return names


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
