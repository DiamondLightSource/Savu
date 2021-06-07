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


def find_synopsis(dclass):
    """
    Finds the parameters list from the docstring
    """
    mod_doc_lines = _get_doc_lines(sys.modules[dclass.__module__].__doc__)
    return _parse_synopsis(mod_doc_lines)


def _parse_synopsis(mod_doc_lines):
    syn_regexp = re.compile(r"^:synopsis: \s?(?P<synopsis>.*[^ ])$")
    synopsis, idx2 = __find_regexp(syn_regexp, mod_doc_lines)
    synopsis = "" if not synopsis else synopsis[0] + "."
    return synopsis


def _get_doc_lines(doc):
    if not doc:
        return [""]
    return [" ".join(l.strip(" .").split()) for l in doc.split("\n")]


def __find_regexp(regexp, str_list):
    args = [regexp.findall(s) for s in str_list]
    index = [i for i in range(len(args)) if args[i]]
    args = [arg[0] for arg in args if len(arg)]
    return args, index


def remove_new_lines(in_string):
    """Remove new lines between text"""
    out_string = in_string
    if out_string:
        out_string = in_string.splitlines()
        out_string = [l.strip() for l in out_string]
        out_string = " ".join(out_string)
    return out_string


def load_yaml_doc(doc):
    """Load in the yaml format. Call yaml_utils.py

    Parameters
    ----------
    lines : str
        String of information

    Returns
    ----------
    all_params: OrderedDict
        Ordered dict of parameters

    """
    # not all Savu dtypes are valid yaml syntax so convert them all to strings
    lines = doc.split('\n')
    doc = ""
    for i, l in enumerate(lines):
        split = (l.split('dtype:', 1))
        if len(split) == 2:
            dtype = split[1].lstrip().rstrip()
            if dtype:
                if not dtype[0] == "'" and not dtype[0] == '"':
                    l = l.replace(dtype, "'" + dtype + "'")
            else:
                print(f"Empty dtype entry for this plugin"
                      f" tools file on line {i}")
        doc += l + "\n"
    all_params = ""
    try:
        all_params = yu.read_yaml_from_doc(doc)
    except Exception as e:
        print("\nError reading the yaml structure from Yaml Utils.\n %s" % e)
    return all_params
