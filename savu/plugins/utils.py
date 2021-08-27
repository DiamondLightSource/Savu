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
import numpy as np

from savu.plugins.loaders.utils.my_safe_constructor import MySafeConstructor

# can I remove these from here?

load_tools = {}
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
    if clazz.__module__.split(".")[0] != "savu":
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
    """Get an instance of the plugin class and populate default parameters.

    :param plugin_name: Name of the plugin to import
    :type plugin_name: str.
    :returns:  An instance of the class described by the named plugin.
    """
    logging.debug("Importing the module %s", plugin_name)
    instance = load_class(plugin_name)()
    instance.initialise(params, exp, check=check)
    return instance


def _get_cls_name(name):
    return "".join(x.capitalize() for x in name.split(".")[-1].split("_"))


def load_class(name, cls_name=None):
    """Returns an instance of the class associated with the module name.

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


def get_tools_class(plugin_tools_id, cls=None):
    if plugin_tools_id == "savu.plugins.plugin_tools":
        plugin_tools_id = "savu.plugins.base_tools"

    # determine Savu base path
    path_name = plugin_tools_id.replace(".", "/")
    savu_path = os.path.join(savu.__path__[0], "..")
    if len(path_name.split("plugin_templates")) > 1:
        file_path = os.path.join(
            savu_path, "plugin_examples", path_name + ".py")
    else:
        file_path = os.path.join(savu_path, path_name + ".py")

    if os.path.isfile(file_path):
        if cls:
            return load_class(plugin_tools_id)(cls)
        else:
            return load_class(plugin_tools_id)


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
    user_path = [os.path.join(os.path.expanduser("~"), "savu_plugins")]
    env_paths = os.getenv("SAVU_PLUGINS_PATH", "").replace(" ", "").split(":")
    templates = "../plugin_examples/plugin_templates"
    eg_path = [os.path.join(savu.__path__[0], templates)] if examples else []

    for ppath in env_paths + user_path + eg_path:
        if os.path.exists(ppath):
            plugins_paths[ppath] = os.path.basename(ppath) + "."
            if ppath not in sys.path:
                sys.path.append(os.path.dirname(ppath))

    return plugins_paths


def is_template_param(param):
    """Identifies if the parameter should be included in an input template
    and returns the default value of the parameter if it exists.
    """
    start = 0
    ptype = "local"
    if isinstance(param, str):
        param = param.strip()
        if not param.split("global")[0]:
            ptype = "global"
            start = 6
        first, last = param[start], param[-1]
        if first == "<" and last == ">":
            param = param[start + 1 : -1]
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

    fname = tempfile.mkdtemp() + "/unwanted_prints.txt"
    sys.stdout = open(fname, "w")


def enablePrint():
    """ Enable printing to stdout """
    sys.stdout = sys.__stdout__


def parse_config_string(string):
    regex = r"[\[\]\, ]+"
    split_vals = [_f for _f in re.split(regex, string) if _f]
    delimitors = re.findall(regex, string)
    split_vals = [repr(a.strip()) for a in split_vals]
    zipped = itertools.zip_longest(delimitors, split_vals)
    string = "".join([i for l in zipped for i in l if i is not None])
    try:
        return ast.literal_eval(string)
    except ValueError:
        return ast.literal_eval(parse_array_index_as_string(string))


def parse_array_index_as_string(string):
    p = re.compile(r"'\['")
    for m in p.finditer(string):
        offset = m.start() - count + 3
        end = string[offset:].index("']") + offset
        string = string[:end] + "]'" + string[end + 2 :]
    string = string.replace("'['", "[")
    return string


def param_to_str(param_name, keys):
    """Check the parameter is within the provided list and
    return the string name.
    """
    if param_name.isdigit():
        param_name = int(param_name)
        if param_name <= len(keys):
            param_name = keys[param_name - 1]
        else:
            raise ValueError(
                "This parameter number is not valid for this plugin"
            )
    elif param_name not in keys:
        raise Exception("This parameter is not present in this plug in.")

    return param_name


def set_order_by_visibility(parameters, level=False):
    """Return an ordered list of parameters depending on the
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
        if v["display"] == "on":
            if v["visibility"] == "datasets":
                data_keys.append(k)
            if v["visibility"] == "basic":
                basic_keys.append(k)
            if v["visibility"] == "intermediate":
                interm_keys.append(k)
            if v["visibility"] == "advanced":
                adv_keys.append(k)
    if level:
        if level == "datasets":
            keys = data_keys
        elif level == "basic":
            keys = basic_keys
        elif level == "intermediate":
            keys = basic_keys + interm_keys + data_keys
        elif level == "advanced":
            keys = basic_keys + interm_keys + adv_keys + data_keys
        else:
            keys = basic_keys + interm_keys + adv_keys + data_keys
    else:
        keys = basic_keys + interm_keys + adv_keys + data_keys

    return keys


def convert_multi_params(param_name, value):
    """Check if value is a multi parameter and check if each item is valid.
    Change from the input multi parameter string to a list

    :param param_name: Name of the parameter
    :param value: Parameter value
    :return: List or unchanged value
    """
    error_str = ""
    multi_parameters = (
        isinstance(value, str) and (";" in value) and param_name != "preview"
    )
    if multi_parameters:
        value = value.split(";")
        isdict = re.findall(r"[\{\}]+", value[0])
        if ":" in value[0] and not isdict:
            seq = value[0].split(":")
            try:
                seq = [ast.literal_eval(s) for s in seq]
                if len(value) == 0:
                    error_str = (
                        f"No values for tuned parameter "
                        f"'{param_name}' ensure start:stop:step; values "
                        f"are valid"
                    )
                elif len(seq) == 2:
                    value = list(np.arange(seq[0], seq[1]))
                elif len(seq) > 2:
                    value = list(np.arange(seq[0], seq[1], seq[2]))
                else:
                    error_str = "Ensure start:stop:step; values are valid."
                if not value:
                    # Don't allow an empty list
                    raise ValueError
            except:
                error_str = "Ensure start:stop:step; values are valid."
        val_list = (
            parse_config_string(value) if isinstance(value, str) else value
        )
        # Remove blank list entries
        # Change type to int, float or str
        val_list = [_dumps(val) for val in value if val]
        value = val_list
    return value, error_str


def _dumps(val):
    """Replace any missing quotes around variables
    Change the string to an integer, float, tuple, list, str, dict
    """
    import yaml
    # Prevent conversion from on/off to boolean
    yaml.SafeLoader.add_constructor(
        "tag:yaml.org,2002:bool", MySafeConstructor.add_bool
    )
    if isinstance(val, str):
        try:
            # Safely evaluate an expression node or a string containing
            # a Python literal or container display
            value = ast.literal_eval(val)
            return value
        except Exception:
            pass
        try:
            isdict = re.findall(r"[\{\}]+", val)
            val = _sexagesimal_check(val, isdict, remove=False)
            value = yaml.safe_load(val)
            return _sexagesimal_check(value, isdict)
        except Exception:
            val = _sexagesimal_check(val, isdict)
            pass
        try:
            isdict = re.findall(r"[\{\}]+", val)
            # Matches { } between one and unlimited number of times
            if isdict:
                if isinstance(val, dict):
                    value_dict = {}
                    for k, v in val.items():
                        v = v.replace("[", "'[").replace("]", "]'")
                        value_dict[k] = _dumps(
                            yaml.safe_load(v)
                        )
                    return value_dict
                else:
                    value = val.replace("[", "'[").replace("]", "]'")
                    return _dumps(yaml.safe_load(value))
            else:
                value = parse_config_string(val)
                return value
        except Exception:
            if len(val.split(";")) > 1:
                value = val
                return value
            else:
                raise Exception("Invalid string %s" % val)
    else:
        value = val
    return value


def _sexagesimal_check(val, isdict, remove=True):
    """To avoid sexagesimal values being evaluated, replace colon
    values temporarily

    :param val:
    :param isdict: True if braces {} found
    :return: value
    """
    if isinstance(val, str) and not isdict:
        if remove:
            val = val.replace(":?", ":")
        else:
            val = val.replace(":", ":?")
    return val


def check_valid_dimension(dim, prev_list):
    """Check the dimension is within the correct range"""
    if not 0 < dim < 21:
        raise Exception("Please use a dimension between 1 and 20.")
    if prev_list and (dim > len(prev_list)):
        raise Exception(
            "You have not specified enough dimensions "
            "inside the preview parameter."
        )
    return True


def is_slice_notation(value):
    """Return True if the value is made up of multiple"""
    return isinstance(value, str) and (":" in value)


def create_dir(file_path):
    """Check if directories provided exist at this file path. If they don't
    create the directories.
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def indent_multi_line_str(text, indent_level=1, justify=False):
    text = text.split("\n")
    # Remove additional spacing on the left side so that text aligns
    if justify is False:
        text = [(" " * 4 * indent_level) + line for line in text]
    else:
        text = [(" " * 4 * indent_level) + line.lstrip() for line in text]
    text = "\n".join(text)
    return text


def indent(text, indent_level=1):
    text = (" " * 4 * indent_level) + text
    return text


def sort_alphanum(_list):
    """Sort list numerically and alphabetically
    *While maintaining original list value types*

    :param _list: Input list to be sorted
    :return: List sorted by number and letter alphabetically
    """
    return sorted(_list, key=_alphanum)


def _str_to_int(_str):
    """Convert the input str to an int if possible

    :param _str: input string
    :return: integer if text is a digit, else string
    """
    return int(_str) if _str.isdigit() else _str


def _alphanum(_str):
    """Split string into numbers and letters

    :param _str:
    :return: list of numbers and letters
    """
    char_list = re.split("([0-9]+)", _str)
    return [_str_to_int(c) for c in char_list]
