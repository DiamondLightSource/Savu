# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: update_template
   :platform: Unix
   :synopsis: Update template

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import argparse

import savu.plugins.loaders.utils.yaml_utils as yu


def arg_parser():
    """ Arg parser for command line arguments.
    """
    parser = argparse.ArgumentParser(prog='update_template')
    parser.add_argument('template', help='Input template file.')
    parser.add_argument('entry', help='the plugin entry')
    parser.add_argument('key', help='The parameter key.')
    parser.add_argument('value', help='The parameter value.')
    return parser.parse_args()


def update_template(filename, entry, key, val):
    template = yu.read_yaml(filename)
    entry = _string_to_val(entry)
    val = _string_to_val(val)
    template[entry][list(template[entry].keys())[0]][key] = val

    with open(filename, 'w') as stream:
        yu.dump_yaml(template, stream)


def _string_to_val(string):
    if string.isdigit():
        return (int(string))
    try:
        return float(string)
    except ValueError:
        return string

if __name__ == '__main__':
    arg = arg_parser()
    update_template(arg.template, arg.entry, arg.key, arg.value)
