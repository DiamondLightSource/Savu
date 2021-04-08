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
.. module:: parameter_utils
   :platform: Unix
   :synopsis: Parameter utilities

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import re
import h5py
import posixpath
import numpy as np
import configparser

from colorama import Fore

import savu.plugins.loaders.utils.yaml_utils as yu
import savu.plugins.utils as pu


def _preview(value):
    """ preview value """
    parameter_valid = False
    if _list(value):
        if all(_preview_dimension(dimension_value) for dimension_value in value):
            parameter_valid = True
    elif _emptylist(value):
        parameter_valid = True
    return parameter_valid


def _preview_dimension(value):
    """ Check the full preview parameter value """
    import savu.plugins.utils as pu
    parameter_valid = False
    if _string(value):
        slice_range = [*range(1,5)]
        slice_str = [":"*n for n in slice_range]
        if value in slice_str:
            # If : notation is used, accept this
            parameter_valid = True
        elif ":" in value:
            if _split_notation_is_valid(value):
                parameter_valid = True
        elif _preview_dimension_singular(value):
                parameter_valid = True
    elif _integer(value) or _float(value):
        parameter_valid = True
    return parameter_valid


def _split_notation_is_valid(value):
    """Check if the start step stock chunk entries are valid

    :param value: The value to check
    :return: parameter_valid True if the split notation is valid
    """
    split_notation_valid = False
    count_colon = value.count(":")
    if count_colon < 4:
        # Only allow 4 colons, start stop step block
        start_stop_split = value.split(":")
        type_list = [pu._dumps(v) for v in start_stop_split if v]
        if all(_preview_dimension_singular(item) for item in type_list):
            split_notation_valid = True
    return split_notation_valid


def _preview_dimension_singular(value):
    """ Check the singular value within the preview dimension"""
    parameter_valid = False
    if _string(value):
        string_valid = re.fullmatch("(mid|end|[^a-zA-z])+", value)
        # Check that the string does not contain any letters [^a-zA-Z]
        # If it does contain letters, mid and end are the only keywords allowed
        if string_valid:
            try:
                # Attempt to evaluate the provided equation
                temp_value = _preview_eval(value)
                if _integer(temp_value) or _float(temp_value):
                    parameter_valid = True
            except Exception:
                print("There was an error with your dimension value input.")
        else:
            print('If you are trying to use an expression, '
                  'please only use mid and end command words.')
    elif _integer(value) or _float(value):
        parameter_valid = True
    return parameter_valid


def _preview_eval(value):
    """ Evaluate with mid and end"""
    mid = 0
    end = 0
    return eval(value,{"__builtins__":None},{"mid":mid,"end":end})


def _intlist(value):
    """ A list containing integer values """
    parameter_valid = False
    if isinstance(value, list):
        if value:
            # If the list is not empty
            if all(_integer(item) for item in value):
                parameter_valid = True
    return parameter_valid


def _stringlist(value):
    """ A list containing string values """
    parameter_valid = False
    if isinstance(value, list):
        if value:
            # If the list is not empty
            if all(_string(item) for item in value):
                parameter_valid = True
    return parameter_valid


def _numlist(value):
    """ int or float list """
    parameter_valid = False
    if isinstance(value, list):
        if value:
            # If the list is not empty
            if all(_float(item) for item in value):
                parameter_valid = True
    return parameter_valid


def _emptylist(value):
    """ empty list """
    parameter_valid = False
    if isinstance(value, list):
        if len(value) == 0:
            # If the list is empty
            parameter_valid = True
    return parameter_valid


def _range(value):
    """range"""
    parameter_valid = False
    if isinstance(value, tuple):
        if len(value) == 2:
            if _float(value[0]) and _float(value[1]):
                parameter_valid = True
        else:
            print(Fore.RED + "Please enter two values." + Fore.RESET)
    elif _numlist(value):
        if len(value) == 2:
            if _float(value[0]) and _float(value[1]):
                parameter_valid = True
        else:
            print(Fore.RED + "Please enter two values." + Fore.RESET)
    return parameter_valid


def _yamlfilepath(value):
    """ yaml_file_path """
    parameter_valid = False
    if _string(value):
        if os.path.isfile(value):
            # Make sure that the file path exists
            file_path_str = value
            if _yaml_file_is_valid(file_path_str):
                parameter_valid = True
        elif _savufilepath(value):
            # If the file path is not valid, try prepending the savu base path
            savu_base_path = \
                os.path.dirname(os.path.realpath(__file__)).split('scripts')[0]
            file_path_str = savu_base_path + value
            if _yaml_file_is_valid(file_path_str):
                parameter_valid = True
    return parameter_valid


def _yaml_file_is_valid(file_path_str):
    """Try to read the yaml file at the provided file path (file_path_str)
    """
    parameter_valid = False
    with open(file_path_str, 'r') as f:
        errors = yu.check_yaml_errors(f)
        try:
            yu.read_yaml(file_path_str)
            # If the yaml file is read in without errors, then the
            # file path is a valid entry
            parameter_valid = True
        except:
            # Print relevant errors if there is an exception.
            # Some errors may not be serious enough to prevent the yaml
            # file from being read correctly.
            if errors:
                print("There were some errors with your yaml file structure.")
                for e in errors:
                    print(e)
    return parameter_valid


def _intgroup(value):
    """ [path, int_path, int] """
    parameter_valid = False
    try:
        if _list(value):
            entries = value
        if len(entries) == 3:
            file_path = entries[0]

            if _filepath(file_path):
                int_path = entries[1]
                with h5py.File(file_path, "r") as hf:
                    int_path_valid = _check_internal_path(hf, int_path)
                    if int_path_valid:
                        try:
                            compensation_fact = entries[2]
                            parameter_valid = _integer(compensation_fact)
                        except (Exception, ValueError):
                            print("The compensation factor is not an integer.")
        else:
            print(Fore.RED + "Please enter three parameters." + Fore.RESET)
    finally:
        return parameter_valid


def _check_internal_path(hf, int_path):
    """ Check if the internal path is valid"""
    parameter_valid = False
    try:
        # Hdf5 dataset object
        int_data = hf.get(int_path)
        if int_data is None:
            print("There is no data stored at that internal path.")
        else:
            # Internal path is valid, check data is present
            int_data = np.array(int_data)
            if int_data.size >= 1:
                parameter_valid = True
    except AttributeError:
        print("Attribute error.")
    except:
        print(
            Fore.BLUE + "Please choose another interior" " path."
            + Fore.RESET
        )
        print("Example interior paths: ")
        for group in hf:
            for subgroup in hf[group]:
                subgroup_str = "/" + group + "/" + subgroup
                print(u"\t" + subgroup_str)
        raise
    return parameter_valid


def _intgroup1(value):
    """ [int_path, int] """
    parameter_valid = False
    try:
        if _list(value):
            entries = value
        if len(entries) == 2:
            int_path = entries[0]
            if _intpathway(int_path):
                try:
                    scale_fact = int(entries[1])
                    parameter_valid = _integer(scale_fact)
                except (Exception, ValueError):
                    print("The scale factor is not an integer.")
        else:
            print(Fore.RED + "Please enter two parameters." + Fore.RESET)
    finally:
        return parameter_valid


def _directory(value):
    """ directory """
    parameter_valid = False
    # take the directory from the path
    # path = os.path.dirname(value)
    path = value if value else "."
    if os.path.isdir(path):
        parameter_valid = True
    return parameter_valid


def _filepath(value):
    """ file path """
    parameter_valid = False
    if _string(value):
        if os.path.isfile(value):
            parameter_valid = True
        elif _savufilepath(value):
            parameter_valid = True
    return parameter_valid


def _savufilepath(value):
    """ A file path inside the Savu directory"""
    parameter_valid = False
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('scripts')[0]
    if _string(value):
        if os.path.isfile(savu_base_path+value):
            parameter_valid = True
    return parameter_valid


def _intpathway(value):
    # Interior file path
    parameter_valid = False
    # Could check if valid, but only if file_path known for another parameter
    if _string(value):
        parameter_valid = True
    return parameter_valid


def _configfilepath(value):
    """ Check if the value is a config file """
    parameter_valid = False
    if _filepath(value):
        filetovalidate = configparser.ConfigParser()
        filetovalidate.read(value)
        content = filetovalidate.sections()
        if content:
            parameter_valid = True
    return parameter_valid


def _filename(value):
    """Check if the value is a valid filename string"""
    parameter_valid = False
    if _string(value):
        filename = posixpath.normpath(value)
        # Normalise the pathname by collapsing redundant separators and
        # references so that //B, A/B/, A/./B and A/../B all become A/B.
        _os_alt_seps = list(sep
                            for sep in [os.path.sep, os.path.altsep]
                            if sep not in (None, "/"))
        # Find which separators the operating system provides, excluding slash
        for sep in _os_alt_seps:
            if sep in filename:
                return False
        # If path is an absolute pathname. On Unix, that means it begins with
        # a slash, on Windows that it begins with a (back)slash after removing
        # drive letter.
        if os.path.isabs(filename) or filename.startswith("../"):
            print(
                "Please make sure the filename is absolute and doesn't"
                " change directory."
            )
            return False
        parameter_valid = True
    return parameter_valid


def _nptype(value):
    """Check if the value is a numpy data type. Return true if it is."""
    parameter_valid = False
    if (value in np.typecodes) or (value in np.sctypeDict.keys()):
        parameter_valid = True
    return parameter_valid


def _integer(value):
    parameter_valid = False
    if _boolean(value):
        # Prevent boolean from being accepted as an integer value of 1 or 0
        parameter_valid = False
    elif isinstance(value, (int, np.integer)):
        parameter_valid = True
    return parameter_valid


def _positive_integer(value):
    parameter_valid = False
    if _integer(value):
        if value > 0:
            parameter_valid = True
    return parameter_valid


def _boolean(value):
    parameter_valid = False
    if isinstance(value, bool):
        parameter_valid = True
    elif value == "true" or value == "false":
        parameter_valid = True
    return parameter_valid


def _string(value):
    parameter_valid = False
    if isinstance(value, str):
        parameter_valid = True
    return parameter_valid


def _float(value):
    parameter_valid = False
    if isinstance(value, (float, np.float)):
        parameter_valid = True
    elif _integer(value):
        # Allow integer values as well
        float(value)
        parameter_valid = True
    return parameter_valid


def _tuple(value):
    parameter_valid = False
    if isinstance(value, tuple):
        parameter_valid = True
    return parameter_valid


def _dict(value):
    parameter_valid = False
    if isinstance(value, dict):
        parameter_valid = True
    return parameter_valid


def _int_float_dict(value):
    """Dictionary to hold integer keys and float values only
    {integer:float}
    """
    parameter_valid = False
    if isinstance(value, dict):
        if all(_integer(k) for k in value.keys()):
            if all(_float(v) for v in value.values()):
                parameter_valid = True
            else:
                print("Ensure dictionary values are floats.")
        else:
            print("Ensure dictionary keys are integers.")
    return parameter_valid


def _list(value):
    # List of digits or strings
    parameter_valid = False
    if isinstance(value, list):
        # This is a list of integer or float values
        if value:
            # If the list is not empty
            parameter_valid = True
    return parameter_valid


# If you are editing the type dictionary, please update the documentation
# file dev_guides/dev_plugin.rst and the files short_parameter_key.yaml
# and parameter_key.yaml, inside doc/source/files_and_images/plugin_guides/
# to provide guidance for plugin creators

type_dict = {
    "preview": _preview,
    "int_list": _intlist,
    "string_list": _stringlist,
    "num_list": _numlist,
    "empty_list": _emptylist,
    "range": _range,
    "yaml_file_path": _yamlfilepath,
    "file_int_path_int": _intgroup,
    "int_path_int": _intgroup1,
    "filepath": _filepath,
    "savufilepath": _savufilepath,
    "directory": _directory,
    "int_path": _intpathway,
    "config_file_path": _configfilepath,
    "filename": _filename,
    "nptype": _nptype,
    "int": _integer,
    "pos_int": _positive_integer,
    "bool": _boolean,
    "str": _string,
    "float": _float,
    "tuple": _tuple,
    "list": _list,
    "dict": _dict,
    "int_float_dict": _int_float_dict,
}

type_error_dict = {
    "preview": "preview slices",
    "int_list": "list of integers",
    "string_list": "list of strings",
    "num_list": "list of numbers",
    "empty_list": "empty list",
    "range": "range'. For example '<value 1>, <value 2>",
    "yaml_file_path": "yaml file path",
    "file_int_path_int": "[filepath, interior file path, int]",
    "int_path_int": "[interior file path, int]",
    "filepath": "filepath",
    "savufilepath": "filepath within the savu directory",
    "directory": "directory",
    "int_path": "string",
    "config_file_path": "configuration file path",
    "filename": "file name",
    "nptype": "numpy data type",
    "int": "integer",
    "pos_int": "positive integer",
    "bool": "boolean",
    "str": "string",
    "float": "float/integer",
    "tuple": "tuple",
    "list": "list",
    "dict": "dict",
    "int_float_dict": "{int:float}",
}


def is_valid(param_name, value, current_parameter_details):
    """Check if the parameter value (value) is a valid data type
    for the parameter (param_name)

    Check if the value matches the default value.
    Then type check, followed by a check on whether it is present in options
    If the items in options have not been type checked, or have errors,
    it may cause problems.

    :param param_name: The name of the parameter
    :param value: The new value of the parameter
    :param current_parameter_details: Dictionary of information about the
      parameter, such as description, dtype, default
    :return: boolean True if the value is a valid parameter value

    """
    option_error_str = ""
    type_error_str = ""

    dtype = current_parameter_details["dtype"]
    default_value = current_parameter_details["default"]
    # If a default value is used, this is a valid option
    pvalid = _check_default(value, default_value)

    if pvalid is False:
        if isinstance(dtype, list):
            # If there are multiple possible types
            for individual_type in dtype:
                # Errors can be overwritten as later types may match the value type
                pvalid, type_error_str = _check_type(
                                            individual_type,
                                            param_name,
                                            value,
                                            current_parameter_details)
                if pvalid is True:
                    # If the value type matches one of the possible types then exit
                    break
        else:
            pvalid, type_error_str = _check_type(dtype,
                                        param_name,
                                        value,
                                        current_parameter_details)
        # Then check if the option is valid
        if not is_multi_param(param_name, value):
            # If it is a multi parameter, each item is checked individually
            pvalid, option_error_str = _check_options(
                                            current_parameter_details,
                                            value,
                                            pvalid)

    if pvalid is False:
        # If an option error exists then use this error message
        type_error_str = (
            option_error_str
            if option_error_str
            else _error_message(dtype, param_name)
        )

    return pvalid, type_error_str


def _check_type(dtype, param_name, value, current_parameter_details):
    """Check if the provided value matches the required date type

    :param dtype: The required data type
    :param param_name: The parameter name
    :param value: The new value
    :param current_parameter_details: Paramter detail dictionary
    :return: pvalid, True if the value type matches the required dtype
             type_error_str, Error message
    """
    type_error_str = ""
    pvalid = False
    if dtype not in type_dict.keys():
        type_error_str = "That type definition is not configured properly."
    elif is_multi_param(param_name, value):
        # If there are multiple parameters, check each individually
        pvalid, type_error_str = _check_multi_params(
            param_name, value, current_parameter_details
        )
    else:
        pvalid = type_dict[dtype](value)
    return pvalid, type_error_str


def _check_multi_params(param_name, value, current_parameter_details):
    """Check if value is a multi parameter and check if each item is valid.
    Change from the input multi parameter string to a list

    :param param_name: Name of the parameter
    :param value: Parameter value
    :param current_parameter_details: Parameter dictionary
    :return: boolean True if all parameters are valid
             An error string
    """
    type_error_str = ""
    parameter_valid = False
    if is_multi_param(param_name, value):
        val_list, type_error_str = pu.convert_multi_params(param_name, value)
        if not type_error_str:
            for item in val_list:
                parameter_valid, type_error_str = is_valid(
                    param_name, item, current_parameter_details
                )
                if parameter_valid is False:
                    # If one value inside the list is not valid, then return false
                    break

    return parameter_valid, type_error_str


def is_multi_param(param_name, value):
    """Return True if the value is made up of multiple parameters"""
    return (
        _string(value) and (";" in value) and param_name != "preview"
    )


def _check_default(value, default_value):
    """Return true if the new value is either a match for the default
    parameter value or the string 'default'
    """
    default_present = False
    if (
        default_value == str(value)
        or default_value == value
        or value == "default"
        or str(default_value) == str(value)
    ):
        default_present = True
    return default_present


def _check_options(current_parameter_details, value, pvalid):
    """Check if the input value matches one of the valid parameter options"""
    option_error_str = ""
    options = current_parameter_details.get("options") or {}
    if len(options) >= 1:
        if value in options or str(value) in options:
            pvalid = True
        else:
            pvalid = False
            option_error_str = (
                "That does not match one of the required options."
            )
            option_error_str += Fore.CYAN + "\nSome options are:\n"
            option_error_str += "\n".join(options) + Fore.RESET
    return pvalid, option_error_str


def _error_message(dtype, param_name):
    """Create an error message"""
    if isinstance(dtype, list):
        type_options = "' or '".join([str(type_error_dict[t]) for t in dtype])
        error_str = f"Your input for the parameter '{param_name}' must match" \
                    f" the type '{type_options}'."
    else:
        error_str = f"Your input for the parameter '{param_name}' must " \
                    f"match the type '{type_error_dict[dtype]}'."
    return error_str


def _gui_error_message(dtype, param_name):
    """Create an error string for the GUI
    Remove the paramter name, as the GUI message will be displayed below
    each paramter input box"""
    if isinstance(dtype, list):
        type_options = "' or '".join([str(t) for t in dtype])
        error_str = f"Type must match '{type_options}'."
    else:
        error_str = f"Type must match '{type_error_dict[dtype]}'."
    return error_str
