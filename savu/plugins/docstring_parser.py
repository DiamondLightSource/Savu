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
.. module:: docstring_parser
   :platform: Unix
   :synopsis: Parser for the docstring to interpret parameters and plugin info.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import sys
import re
import savu.plugins.loaders.utils.yaml_utils as yu
import os

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

    mod_doc_lines = _get_doc_lines(sys.modules[dclass.__module__].__doc__)
    lines = _get_doc_lines(docstring)

    return _parse_args(mod_doc_lines, lines)


def _load_yaml(docstring):
    """
    Load the docstring and read in the yaml format. Call yaml_utils.py
    ----------
    Parameters:
            - docstring: String of information
    ----------
    Return:
            - param_entry: Ordered dict of parameters
            - verbose: Further description
            - warning:
    """
    all_params = ''
    synopsis = ''
    warning = ''
    verbose = ''
    if os.path.isfile(docstring):
        text = yu.read_yaml(docstring)
    else:
        print('That is not a yaml file path.')
        #text = yu.read_yaml_from_doc(docstring)
    for doc in text:
        # Each yaml document
        for info in doc:
            all_params = info['parameters']
            # parameter is info['parameters'][0]
            if 'warning' in info.keys():
                warning = info['warning']
            else:
                warning = ''
            if 'verbose' in info.keys():
                verbose = info['verbose']
            else:
                verbose = ''
    return all_params, synopsis, warning, verbose


def _parse_args(mod_doc_lines, lines):
    param_list, user, hide, not_param, param_lines = __get_params(lines)

    warn_regexp = re.compile(r'^:config_warn: \s?(?P<config_warn>.*[^ ])$')
    warn, idx1 = __find_regexp(warn_regexp, lines)
    warn = '' if not warn else '.\n'.join(warn)+'.'
    syn_regexp = re.compile(r'^:synopsis: \s?(?P<synopsis>.*[^ ])$')
    synopsis, idx2 = __find_regexp(syn_regexp, mod_doc_lines)
    synopsis = '' if not synopsis else synopsis[0]+'.'

    info = __find_docstring_info(param_lines+idx1+idx2, lines)

    return {'warn': warn, 'info': info, 'synopsis': synopsis,
            'param': param_list, 'hide_param': hide, 'user_param': user,
            'not_param': not_param}


def _get_doc_lines(doc):
    if not doc:
        return ['']
    return [" ".join(l.strip(' .').split()) for l in doc.split('\n')]


def __get_params(lines):
    fixed_str = '(?P<param>\w+):\s?(?P<doc>\w.*[^ ])\s'\
                + '?Default:\s?(?P<default>.*[^ ])$'
    param_regexp = re.compile('^:param ' + fixed_str)
    param, idx1 = __find_regexp(param_regexp, lines)

    not_param_regexp = re.compile('^:~param (?P<param>\w+):')
    not_param, idx2 = __find_regexp(not_param_regexp, lines)

    hidden_param_regexp = re.compile('^:\*param ' + fixed_str)
    hidden_param, idx3 = __find_regexp(hidden_param_regexp, lines)
    hide_keys = [p[0] for p in hidden_param]

    user_param_regexp = re.compile('^:u\*param ' + fixed_str)
    user_param, idx4 = __find_regexp(user_param_regexp, lines)
    user_keys = [p[0] for p in user_param]

    lines_read = idx1+idx2+idx3+idx4

    param = user_param + param + hidden_param

    param_entry = [{'dtype': type(value), 'name': a[0], 'desc': a[1],
                    'default': value} for a in param for value in [eval(a[2])]]

    return param_entry, user_keys, hide_keys, not_param, lines_read


def __find_regexp(regexp, str_list):
    args = [regexp.findall(s) for s in str_list]
    index = [i for i in range(len(args)) if args[i]]
    args = [arg[0] for arg in args if len(arg)]
    return args, index


def __find_docstring_info(index, str_list):
    info = [str_list[i] for i in range(len(str_list)) if i not in index]
    info = [i for i in info if i]
    info = "" if not info else "\n".join(info) + '.'
    return info
