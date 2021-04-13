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

.. moduleauthor:: Jessica Verschoyle,Nicola Wadeson <scientificsoftware@diamond.ac.uk>

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
    valid = _typelist(_preview_dimension, value)
    if not valid:
        valid = _emptylist(value)
    return valid


def _typelist(func, value):
    if isinstance(value, list):
        if value:
            return all(func(item) for item in value)
    return False


def _preview_dimension(value):
    """ Check the full preview parameter value """
    import savu.plugins.utils as pu
    if _string(value):
        slice_range = [*range(1,5)]
        slice_str = [":"*n for n in slice_range]
        if value in slice_str:
            # If : notation is used, accept this
            valid = True
        elif ":" in value:
            valid = _split_notation_is_valid(value)
        else:
            valid = _preview_dimension_singular(value)
    else:
        valid = _float(value)
    return valid


def _split_notation_is_valid(value):
    """Check if the start step stock chunk entries are valid

    :param value: The value to check
    :return: parameter_valid True if the split notation is valid
    """
    split_notation_valid = False
    if value.count(":") < 4:
        # Only allow 4 colons, start stop step block
        start_stop_split = value.split(":")
        type_list = [pu._dumps(v) for v in start_stop_split if v]
        split_notation_valid = _typelist(_preview_dimension_singular,
                                         type_list)
    return split_notation_valid


def _preview_dimension_singular(value):
    """ Check the singular value within the preview dimension"""
    valid = False
    if _string(value):
        string_valid = re.fullmatch("(mid|end|[^a-zA-z])+", value)
        # Check that the string does not contain any letters [^a-zA-Z]
        # If it does contain letters, mid and end are the only keywords allowed
        if string_valid:
            try:
                # Attempt to evaluate the provided equation
                temp_value = _preview_eval(value)
                valid = _float(temp_value)
            except Exception:
                print("There was an error with your dimension value input.")
        else:
            print('If you are trying to use an expression, '
                  'please only use mid and end command words.')
    else:
        valid = _float(value)
    return valid


def _preview_eval(value):
    """ Evaluate with mid and end"""
    mid = 0
    end = 0
    return eval(value,{"__builtins__":None},{"mid":mid,"end":end})


def _intlist(value):
    """ A list containing integer values """
    return _typelist(_integer, value)


def _stringlist(value):
    """ A list containing string values """
    return _typelist(_string, value)


def _numlist(value):
    """ int or float list """
    return _typelist(_float, value)


def _emptylist(value):
    """ empty list """
    if isinstance(value, list) and not value:
        return True
    return False


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
    """ yamlfilepath """
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
    yaml_file_valid = False
    with open(file_path_str, 'r') as f:
        errors = yu.check_yaml_errors(f)
        try:
            yu.read_yaml(file_path_str)
            # If the yaml file is read in without errors, then the
            # file path is a valid entry
            yaml_file_valid = True
        except:
            # Print relevant errors if there is an exception.
            # Some errors may not be serious enough to prevent the yaml
            # file from being read correctly.
            if errors:
                print("There were some errors with your yaml file structure.")
                for e in errors:
                    print(e)
    return yaml_file_valid


def _intgroup(value):  # why is this called _intgroup? can we have something like list[filepath, hdffilepath, int]
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
            Fore.BLUE + "Please choose another interior path."
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
    path = value if value else "."
    return os.path.isdir(path)


def _filepath(value):
    """ file path """
    valid = False
    if _string(value):
        valid = os.path.isfile(value)
        if not valid:
            valid = _savufilepath(value)
    return valid


def _savufilepath(value):
    """A file path inside the Savu directory"""
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('scripts')[0]
    if _string(value):
        return os.path.isfile(savu_base_path+value)
    return False


def _intpathway(value):
    """Interior file path"""
    # Could check if valid, but only if file_path known for another parameter
    return _string(value)


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
    # do not use isinstance as this also picks up boolean values
    if type(value) in (int, np.integer):
        return True
    return False


def _positive_integer(value):
    if _integer(value):
        return value > 0
    return False


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
    valid = isinstance(value, (float, np.float))
    if not valid:
        valid = _integer(value)
    return valid


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
    "yamlfilepath": _yamlfilepath,
    "file_int_path_int": _intgroup,
    "int_path_int": _intgroup1,
    "filepath": _filepath,
    "directory": _directory,
    "int_path": _intpathway,
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
    "yamlfilepath": "yaml file path",
    "file_int_path_int": "[filepath, interior file path, int]",
    "int_path_int": "[interior file path, int]",
    "filepath": "filepath",
    "directory": "directory",
    "int_path": "string",
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


def is_valid(param_name, value, param_def):
    """Check if the parameter value (value) is a valid data type
    for the parameter (param_name)

    Check if the value matches the default value.
    Then type check, followed by a check on whether it is present in options
    If the items in options have not been type checked, or have errors,
    it may cause problems.

    :param param_name: The name of the parameter
    :param value: The new value of the parameter
    :param param_def: Parameter definition dictionary, containing e.g.,
        description, dtype, default
    :return: boolean True if the value is a valid parameter value

    """
    error_str = ""
    dtype = param_def["dtype"]
    default_value = param_def["default"]

    # If a default value is used, this is a valid option
    if _check_default(value, default_value):
        return True, error_str

    dtype = dtype if isinstance(dtype, list) else [dtype]
    for atype in dtype:
        pvalid, error_str = _check_type(
            atype, param_name, value, param_def)
        if pvalid:
            break

    return pvalid, error_str

def _check_type(dtype, param_name, value, param_def):
    """Check if the provided value matches the required date type

    :param dtype: The required data type
    :param param_name: The parameter name
    :param value: The new value
    :param param_def: Parameter definition dictionary
    :return: pvalid, True if the value type matches the required dtype
              type_error_str, Error message
    """
    # If this is paramter tuning, check each individually
    if is_multi_param(param_name, value):
        val_list, error_str = pu.convert_multi_params(param_name, value)
        # incorrect parameter tuning syntax
        if error_str:
            return False, error_str

        for val in val_list:
            pvalid, error_str = _check_type(dtype, param_name, val, param_def)

            if not pvalid:
                return pvalid, error_str
    else:
        pvalid = type_dict[dtype](value)

    if not pvalid:
        return pvalid, _error_message(dtype, param_name)

    return _check_options(param_def, value, pvalid)


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


def _check_options(param_def, value, pvalid):
    """Check if the input value matches one of the valid parameter options"""
    option_error_str = ""
    options = param_def.get("options") or {}
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
    each parameter input box
    """
    if isinstance(dtype, list):
        type_options = "' or '".join([str(t) for t in dtype])
        error_str = f"Type must match '{type_options}'."
    else:
        error_str = f"Type must match '{type_error_dict[dtype]}'."
    return error_str
