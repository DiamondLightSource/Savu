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
import copy
import h5py
import posixpath
import numpy as np
import configparser

from colorama import Fore

import savu.plugins.loaders.utils.yaml_utils as yu
import savu.plugins.utils as pu


def _int(value):
    # do not use isinstance as this also picks up boolean values
    if type(value) in (int, np.int_):
        return True
    return False


def _str(value):
    if isinstance(value, str):
        return True
    return False


def _float(value):
    valid = isinstance(value, (float, np.float))
    if not valid:
        valid = _int(value)
    return valid


def _bool(value): # should eventually be a drop-down list
    valid = isinstance(value, bool)
    if not valid and isinstance(value, str):
        return value.lower() == "true" or value.lower() == "false"
    return valid


def _dir(value):
    """ A directory """
    valid = False
    if _str(value):
        valid = os.path.isdir(value)
        if not valid:
            valid = os.path.isdir(_savupath(value))
    return valid


def _filepath(value):
    """ file path """
    valid = False
    if _str(value):
        valid = os.path.isfile(value)
        if not valid:
            valid = os.path.isfile(_savupath(value))
    return valid


def _h5path(value): # Extend this later as we need to know which file to apply the check to
    """ internal path to a hdf5 dataset """
    return _str(value)


def _savupath(value):
    """ A path inside the Savu directory"""
    savu_base_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), '../../')
    split_path = value.split("Savu/")
    if len(split_path) > 1:
        value = os.path.join(savu_base_path, split_path[-1][:])
    return value


def _yamlfilepath(value):
    """ yaml_file """
    # does the filepath exist
    if _str(value):
        if not os.path.isfile(value):
            # is it a file path in Savu folder
            value = _savupath(value)
            if not os.path.isfile(value):
                return False
        return _yaml_is_valid(value)
    return False

def _yaml_is_valid(filepath):
    """Read the yaml file at the provided file path """
    with open(filepath, 'r') as f:
        errors = yu.check_yaml_errors(f)
        try:
            yu.read_yaml(filepath)
            return True
        except:
            if errors:
                print("There were some errors with your yaml file structure.")
                for e in errors:
                    print(e)
    return False

def _nptype(value):
    """Check if the value is a numpy data type. Return true if it is."""
    if _int(value) or _str(value):
        return (value in np.typecodes) or (value in np.sctypeDict.keys())
    return False


def _preview(value):
    """ preview value """
    valid = _typelist(_preview_dimension, value)
    if not valid and _list(value) and not value:
        return True # empty list is allowed
    return valid


def _typelist(func, value):
    if isinstance(value, list):
        if value:
            return all(func(item) for item in value)
    return False


def _preview_dimension(value):
    """ Check the full preview parameter value """
    if _str(value):
        slice_str = [":"*n for n in range(1,5)]
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
    if value.count(":") < 4:
        # Only allow 4 colons, start stop step block
        start_stop_split = value.split(":")
        try:
            type_list = [pu._dumps(v) for v in start_stop_split if v]
            return _typelist(_preview_dimension_singular,
                             type_list)
        except Exception as e:
            print(f"There was an error with your slice notation, '{value}'")
    return False


def _preview_dimension_singular(value):
    """ Check the singular value within the preview dimension"""
    valid = False
    if _str(value):
        string_valid = re.fullmatch("(start|mid|end|[^a-zA-z])+", value)
        # Check that the string does not contain any letters [^a-zA-Z]
        # If it does contain letters, start, mid and end are the only keywords allowed
        if string_valid:
            try:
                # Attempt to evaluate the provided equation
                temp_value = _preview_eval(value)
                valid = _float(temp_value)
            except Exception:
                print("There was an error with your dimension value input.")
        else:
            print('If you are trying to use an expression, '
                  'please only use start, mid and end command words.')
    else:
        valid = _float(value)
    return valid


def _preview_eval(value):
    """ Evaluate with start, mid and end"""
    start = 0
    mid = 0
    end = 0
    return eval(value,{"__builtins__":None},{"start":start,
                                             "mid":mid,
                                             "end":end})


#Replace this with if list combination contains filepath and h5path e.g. list[filepath, h5path, int] then perform this check
def _check_h5path(filepath, h5path):
    """ Check if the internal path is valid"""
    with h5py.File(filepath, "r") as hf:
        try:
            # Hdf5 dataset object
            h5path = hf.get(h5path)
            if h5path is None:
                print("There is no data stored at that internal path.")
            else:
                # Internal path is valid, check data is present
                int_data = np.array(h5path)
                if int_data.size >= 1:
                    return True, ""
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
    return False, "Invalid path %s for file %s" % (h5path, filepath)


def _list(value):
    """ A non-empty list """
    if isinstance(value, list):
        return True
    return False


def _dict(value):
    """ A dictionary """
    return isinstance(value, dict)


def _None(value):
    """ None """
    return value == None  or value == "None"


def _dict_combination(param_name, value, param_def):
    dtype = copy.copy(param_def['dtype'])

    param_def['dtype'] = 'dict'
    # check this is a dictionary
    pvalid, error_str = _check_type(param_name, value, param_def)
    if not pvalid:
        return pvalid, error_str
    param_def['dtype'] = dtype

    return _check_dict_combination(param_name, value, param_def)


def _check_dict_combination(param_name, value, param_def):
    dtype = copy.copy(param_def['dtype'])
    dtype = dtype[len('dict'):]
    dtype = _find_options(dtype, 'dict', '{', '}', ':')

    #special case of empty dict
    if not value:
        if dtype[0] != "":
            error = "The empty dict is not a valid option for %s" % param_name
            return False, error
        else:
            return True, ""

    # check there are only two options - for key and for value:
    if len(dtype) != 2:
        return False, "Incorrect number of dtypes supplied for dictionary"
    return _check_dict_entry_dtype(param_name, value, param_def, dtype)


def _check_dict_entry_dtype(param_name, value, param_def, dtype):
    """ Check that the dict keys and values are of the correct dtype """
    # check the keys
    n_vals = len(value.keys())

    multi_vals = zip(list([dtype[0]] * n_vals), list(value.keys()))
    pvalid, error_str = _is_valid_multi(param_name, param_def, multi_vals)

    if not pvalid:
        # If the keys are not the correct type, break and return False
        return pvalid, error_str

    # check the values:
    multi_vals = zip(list([dtype[1]] * n_vals), list(value.values()))
    return _is_valid_multi(param_name, param_def, multi_vals)


def _options_list(param_name, value, param_def):
    """
    There are multiple options of dtype defined in a list.
    E.g. dtype: [string, int] # dtype can be a string or an integer
    """
    dtype = _find_options(param_def['dtype'])
    for atype in dtype:
        param_def['dtype'] = atype
        pvalid, error_str = is_valid(param_name, value, param_def)
        if pvalid:
            return pvalid, error_str
    return pvalid, _error_message(param_name, dtype)


def _list_combination(param_name, value, param_def):
    """
    e.g.
    (1) list
    (1) list[btype] => any length
    (2) list[btype, btype]  => fixed length (and btype can be same or different)
        - list[int], list[string, string], list[list[string, float], int]
    (3) list[filepath, h5path, int]
    (4) list[[option1, option2]] = list[option1 AND/OR option2]
    """
    dtype = copy.copy(param_def['dtype'])

    # is it a list?
    param_def['dtype'] = 'list'
    pvalid, error_str = _check_type(param_name, value, param_def)
    if not pvalid:
        return pvalid, error_str
    param_def['dtype'] = dtype

    return _check_list_combination(param_name, value, param_def)


def _check_list_combination(param_name, value, param_def):
    dtype = copy.copy(param_def['dtype'])
    # remove outer list from dtype and find separate list entries
    dtype = _find_options(dtype[len('list'):])

    #special case of empty list
    if not value:
        if dtype[0] != "":
            error = "The empty list is not a valid option for %s" % param_name
            return False, error
        else:
            return True, ""

    # list can have any length if btype_list has length 1
    if len(dtype) == 1:
        dtype = dtype*len(value)

    if len(dtype) != len(value):
        return False, f"Incorrect number of list entries for {value}. " \
            f"The required format is {dtype}"

    return _is_valid_multi(param_name, param_def, zip(dtype, value))


def _matched_brackets(string, dtype, bstart, bend):
    start_brackets = [m.start() for m in re.finditer(r'\%s' % bstart, string)]
    end_brackets = [m.start() for m in re.finditer(r'\%s' % bend, string)]
    matched = []
    # Match start and end brackets
    while(end_brackets):
        try:
            end = end_brackets.pop(0)
            idx = start_brackets.index([s for s in start_brackets if s < end][-1])
            start = start_brackets.pop(idx)
            extra = len(dtype) if string[start-4:start] == dtype else 0
        except IndexError as ie:
            raise IndexError(f"Incorrect number of brackets in {string}")
        matched.append((start - extra, end))

    return matched


def _remove_nested_brackets(matched):
    if len(matched) > 1:
        for outer in matched[::-1]:
            for i in range(len(matched[:-1]))[::-1]:
                # Remove if is this bracket inside the outer bracket
                if matched[i][0] > outer[0] and matched[i][1] < outer[1]:
                    matched.pop(i)
    return matched


def _find_options(string, dtype='list', bstart="[", bend="]", split=","):
    string = string[1:-1]
    matched = _matched_brackets(string, dtype, bstart, bend)
    # find and remove nested brackets
    matched = _remove_nested_brackets(matched)
    replace_strings = {}
    # replace statements with place holders containing no commas
    shift = 0
    for i in range(len(matched)):
        replace = string[matched[i][0]-shift:matched[i][1]-shift+1]
        replacement = '$' + str(i)
        replace_strings[replacement] = replace
        string = string.replace(replace, replacement)
        shift = matched[i][1] - matched[i][0] - 1

    options = string.split(split)
    # substitute original statements back in
    for i in range(len(options)):
        if options[i] in replace_strings.keys():
            options[i] = replace_strings[options[i]]

    return options


def _convert_to_list(value):
    return value if isinstance(value, list) else [value]


def _is_valid_multi(param_name, param_def, multi_vals):
    dtype = copy.copy(param_def['dtype'])
    for atype, val in multi_vals:
        param_def['dtype'] = atype
        _check_val = pu._dumps(val)
        pvalid, error_str = is_valid(param_name, _check_val, param_def)
        if not pvalid:
            error_str = "The value %s should be of type %s" % (val, atype)
            return pvalid, error_str
    param_def['dtype'] = dtype
    return True, ""


def is_valid(param_name, value, param_def, check=False):
    """Check if the parameter value is a valid data type for the parameter

    :param param_name: The name of the parameter
    :param value: The new value of the parameter
    :param param_def: Parameter definition dictionary, containing e.g.,
        description, dtype, default
    :return: boolean True if the value is a valid parameter value
    """
    original_dtype = copy.copy(param_def['dtype'])
    # remove all whitespaces from dtype
    param_def['dtype'] = param_def['dtype'].replace(" ", "")

    # If a default value is used, this is a valid option
    # Don't perform this check when checking the default value itself
    if not check:
        if _check_default(value, param_def['default']):
            return True, ""

    dtype = param_def["dtype"]

    # If this is parameter tuning, check each individually
    if is_multi_param(param_name, value):
        return _check_multi_param(param_name, value, param_def)

    if not dtype.split('list[')[0]:
        pvalid, error_str = _list_combination(param_name, value, param_def)
    elif not dtype.split('dict{')[0]:
        pvalid, error_str = _dict_combination(param_name, value, param_def)
    elif not dtype.split('[')[0] and not dtype.split(']')[-1]:
        pvalid, error_str = _options_list(param_name, value, param_def)
    else:
        pvalid, error_str =_check_type(param_name, value, param_def)

    # set dtype back to the original
    param_def['dtype'] = original_dtype
    return pvalid, error_str


def _check_type(param_name, value, param_def):
    """Check if the provided value matches the required date type

    :param param_name: The parameter name
    :param value: The new value
    :param param_def: Parameter definition dictionary
    :return: pvalid, True if the value type matches the required dtype
              type_error_str, Error message
    """
    dtype = param_def['dtype']
    # If this is parameter tuning, check each individually
    try:
        pvalid = globals()["_" + dtype](value)
    except KeyError:
        return False, "Unknown dtype '%s'" % dtype

    pvalid, opt_err = _check_options(param_def, value, pvalid)
    if not pvalid:
        return pvalid, opt_err if opt_err \
            else _error_message(param_name, dtype)

    return True, ""


def _check_multi_param(param_name, value, param_def):
    """ Check each multi parameter value individually

    :param param_name: The parameter name
    :param value: The multi parameter value to check
    :param param_def: The dictionary of parameter definitions
    :return: pvalid True if the value type matches the required dtype
             type_error_str, Error message
    """
    val_list, error_str = pu.convert_multi_params(param_name, value)
    # incorrect parameter tuning syntax
    if error_str:
        return False, error_str
    for val in val_list:
        pvalid, error_str = is_valid(param_name, val, param_def)
        if not pvalid:
            break
    return pvalid, error_str


def is_multi_param(param_name, value):
    """Return True if the value is made up of multiple parameters"""
    return (
        _str(value) and (";" in value) and param_name != "preview"
    )


def _check_default(value, default_value):
    """Return true if the new value is a match for the default
    parameter value
    """
    default_present = False
    if str(default_value) == str(value):
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
            option_error_str += Fore.CYAN + "\nThe options are:\n"
            option_error_str += "\n".join(str(o) for o in options) + Fore.RESET
    return pvalid, option_error_str


def _error_message(param_name, dtype):
    """Create an error message"""
    if isinstance(dtype, list):
        type_options = "' or '".join(
            [str(type_error_dict[t] if t in type_error_dict else t)
                for t in dtype]
        )
        error_str = f"The parameter '{param_name}' does not match" \
                    f" the options: '{type_options}'."
    else:
        error_str = f"The parameter '{param_name}' does not match " \
                    f"the type: '{type_error_dict[dtype]}'."
    return error_str


def _gui_error_message(param_name, dtype):
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


type_error_dict = {
    "preview": "preview slices",
    "yamlfilepath": "yaml filepath",
    "filepath": "filepath",
    "h5path" : "hdf5 path",
    "filename": "file name",
    "dir": "directory",
    "nptype": "numpy data type",
    "int": "integer",
    "bool": "true/false",
    "str": "string",
    "float": "float/integer",
    "list": "list",
    "dict": "dict",
    "None": "None"
}


def is_valid_dtype(dtype):
    """
    Checks if the dtype is defined correctly
    """
    if not dtype.split('list[')[0]:
        pvalid, error_str = _is_valid_list_combination_type(dtype)
    elif not dtype.split('dict{')[0]:
        pvalid, error_str = _is_valid_dict_combination_type(dtype)
    elif not dtype.split('[')[0] and not dtype.split(']')[-1]:
        pvalid, error_str = _is_valid_options_list_type(dtype)
    else:
        if '_' + dtype in globals().keys():
            return True, ""
        else:
            return "False", "The basic dtype %s does not exist" % dtype
    return pvalid, error_str


def _is_valid_list_combination_type(dtype):
    if not dtype:
        return True, "" # the empty list
    if not dtype[-1] == ']':
        return False, "List combination is missing a closing bracket."
    return is_valid_dtype(dtype[len('list['):-1])


def _is_valid_dict_combination_type(dtype):
    if not dtype[-1] == '}':
        return False, "Dict combination is missing a closing bracket"
    dtype = dtype[len('dict{'):-1]
    dtype = _find_options(dtype, 'dict', '{', '}', ':')
    for atype in dtype:
        pvalid, error_str = is_valid_dtype(atype)
        if not pvalid:
            break
    return pvalid, error_str


def _is_valid_options_list_type(dtype):
    if not dtype[-1] == ']':
        return False, "Options list is missing a closing bracket."
    dtype = _find_options(dtype)
    for atype in dtype:
        pvalid, error_str = is_valid_dtype(atype)
        if not pvalid:
            break
    return pvalid, error_str
