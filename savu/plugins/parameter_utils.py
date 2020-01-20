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
.. module:: savu_config.py
   :platform: Unix
   :synopsis: A command line tool for creating Savu plugin lists

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from __future__ import print_function

import os
import h5py
import numpy as np
import configparser

from savu.plugins.utils import parse_config_string as parse_str
from yamllint.config import YamlLintConfig
from yamllint import linter
from colorama import Fore

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from scripts.config_generator.config_utils import error_catcher_valid

@error_catcher_valid
def _intlist(value):
    '''
    ['int']
    '''
    parameter_valid = False
    try:
        value = parse_str(value) if \
            isinstance(value, str) else value
    except:
        print('Error parsing string.')
    # To Do - check preview list
    return parameter_valid

@error_catcher_valid
def _range(value):
    '''range'''
    parameter_valid = False
    entries = value.split(',')
    if len(entries) == 2:
        if isinstance(entries[0], int) and isinstance(entries[1], int):
            parameter_valid = True
    return parameter_valid


@error_catcher_valid
def _yamlfile(value):
    """ yamlfile """
    parameter_valid = False
    if isinstance(value, str):
        config_file = open('/home/glb23482/git_projects/Savu/savu/plugins/loaders/utils/yaml_config.yaml')
        conf = YamlLintConfig(config_file)
        f = open(value)
        gen = linter.run(f, conf)
        errors = list(gen)
        if errors:
            print('There were some errors with your yaml file structure.\n')
            for e in errors:
                print(e)
        else:
            parameter_valid = True
    return parameter_valid


@error_catcher_valid
def _intgroup(value):
    """ [path, int_path, int] """
    parameter_valid = False
    try:
        bracket_value = value.split('[')
        bracket_value = bracket_value[1].split(']')
        entries = bracket_value[0].split(',')
        if len(entries) == 3:
            file_path = entries[0]
            if os.path.isfile(file_path):
                int_path = entries[1]
                hf = h5py.File(file_path, 'r')
                try:
                    # This returns a HDF5 dataset object
                    int_data = hf.get(int_path)
                    if int_data is None:
                        print('\nThere is no data stored at that internal path.')
                    else:
                        int_data = np.array(int_data)
                        if int_data.size >= 1:
                            try:
                                compensation_fact = int(entries[2])
                                if isinstance(compensation_fact, int):
                                    parameter_valid = True
                                else:
                                    print(Fore.BLUE + '\nThe compensation factor is'
                                                      ' not valid.' + Fore.RESET)
                            except ValueError:
                                print('\nThe compensation factor is not an integer.')
                            except Exception:
                                print('There is a problem converting the compensation'
                                      ' factor to an integer.')

                except AttributeError:
                    print('Attribute error.')
                except:
                    print(Fore.BLUE + '\nPlease choose another interior'
                                      ' path.' + Fore.RESET)
                    print('Example interior paths: ')
                    for group in hf:
                        for subgroup in hf[group]:
                            subgroup_str = '/' + group + '/' + subgroup
                            print(u'\t' + subgroup_str)
                    raise
                hf.close()
            else:
                print(Fore.BLUE + '\nThis file does not exist at this'
                                  ' location.' + Fore.RESET)
        else:
            print(Fore.RED + '\nPlease enter three parameters.' + Fore.RESET)
        return parameter_valid
    except ValueError:
        parameter_valid = False
        print('Valid items have a format [<file path>,'
              ' <interior file path>, int].')
    except AttributeError:
        print('You need to place some information inside the square brackets.')
    except Exception as e:
        print(e)


@error_catcher_valid
def _intgroup1(value):
    """ [path, int] """
    parameter_valid = False
    try:
        bracket_value = value.split('[')
        bracket_value = bracket_value[1].split(']')
        entries = bracket_value[0].split(',')
        if len(entries) == 2:
            file_path = entries[0]
            if os.path.isfile(file_path):
                try:
                    scale_fact = int(entries[1])
                    if isinstance(scale_fact, int):
                        parameter_valid = True
                    else:
                        print(Fore.BLUE + '\nThe scale factor is'
                                          ' not valid.' + Fore.RESET)
                except ValueError:
                    print('\nThe scale factor is not an integer.')
                except Exception:
                    print('There is a problem converting the scale'
                          ' factor to an integer.')
            else:
                print(Fore.BLUE + '\nThis file does not exist at this'
                                  ' location.' + Fore.RESET)
        else:
            print(Fore.RED + '\nPlease enter two parameters.' + Fore.RESET)
        return parameter_valid
    except ValueError:
        parameter_valid = False
        print('Valid items have a format [<file path>,'
              ', int].')
    except AttributeError:
        print('You need to place some information inside the square brackets.')
    except Exception as e:
        print(e)


@error_catcher_valid
def _path(value):
    """ path """
    parameter_valid = False
    path = os.path.dirname(value)
    path = path if path else '.'
    if os.path.isdir(path):
        parameter_valid = True
        print('This path is to a directory.')
    elif os.path.isfile(path):
        parameter_valid = True
        print('This path is to a file.')
    else:
        print('Valid items contain numbers, letters and \'/\'')
        file_error = "INPUT_ERROR: Incorrect filepath."
        raise Exception(file_error)
    return parameter_valid


@error_catcher_valid
def _intpathway(value):
    parameter_valid = False
    # Check if the entry is a string
    # Could check if valid, but only if file_path known for another parameter
    if isinstance(value, str):
        parameter_valid = True
    else:
        print('Not a valid string.')
    return parameter_valid


@error_catcher_valid
def _configfile(value):
    parameter_valid = False
    if isinstance(value, str):
        filetovalidate = configparser.ConfigParser()
        filetovalidate.read(value)
        content = filetovalidate.sections()
        if content:
            parameter_valid = True
    else:
        print('Not a valid string.')

    return parameter_valid


@error_catcher_valid
def _nptype(value):
    parameter_valid = False
    if (value in np.typecodes) or (value in np.sctypeDict.keys()):
        parameter_valid = True
    else:
        print('Not a valid numpy data type.')
    return parameter_valid


@error_catcher_valid
def _integer(value):
    parameter_valid = False
    if isinstance(value, int):
        parameter_valid = True
    else:
        print('%s is not a valid integer.' % value)
    return parameter_valid

@error_catcher_valid
def _boolean(value):
    parameter_valid = False
    if isinstance(value, bool):
        parameter_valid = True
    elif value == 'true' or value == 'false':
        parameter_valid = True
    else:
        print('Not a valid boolean.')
    return parameter_valid


@error_catcher_valid
def _string(value):
    parameter_valid = False
    if isinstance(value, str):
        parameter_valid = True
    else:
        print('Not a valid string.')
    return parameter_valid


@error_catcher_valid
def _float(value):
    parameter_valid = False
    if isinstance(value, float):
        parameter_valid = True
    else:
        print('Not a valid float.')
    return parameter_valid


@error_catcher_valid
def _tuple(value):
    parameter_valid = False
    if isinstance(value, tuple):
        parameter_valid = True
    else:
        print('Not a valid tuple.')
    return parameter_valid


type_list = {'[int]': _intlist,
            'range': _range,
            'yaml_file': _yamlfile,
            '[path, int_path, int]': _intgroup,
            '[path, int]': _intgroup1,
            'path': _path,
            'int_path': _intpathway,
            'config_file': _configfile,
            'nptype': _nptype,
            'int': _integer,
            'bool': _boolean,
            'str': _string,
            'float': _float,
            'tuple': _tuple}


def is_valid(ptype_t, value):
    # comp = Completer(commands=type_list, plugin_list=pu.plugins)
    ptype = ptype_t
    if ptype not in type_list:
        print("That type is not valid.")
        ptype_res = False
    else:
        ptype_res = type_list[ptype](value)

    return ptype_res
