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
.. module:: hdf5_template_extractor
   :platform: Unix
   :synopsis: Extract hdf5 templates

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import sys
import argparse

from savu.data.meta_data import MetaData
from scripts.config_generator.content import Content
from savu.plugins.loaders.yaml_converter import YamlConverter


def arg_parser():
    """ Arg parser for command line arguments.
    """
    parser = argparse.ArgumentParser(prog='update_template')
    parser.add_argument('nxsfile', help='The nexus file')
    key_help = 'Full stop separated key for dictionary entry'
    parser.add_argument("-k", "--key", help=key_help, default=None)
    return parser.parse_args()


def get_parameter_value(nxsfile, plugin_name, plugin_param):
    content = Content()
    content.fopen(nxsfile)
    plist = content.plugin_list.plugin_list

    found_params = []
    for plugin in plist:
        if plugin['name'] == plugin_name:
            if plugin_param in list(plugin['data'].keys()):
                found_params.append(plugin['data'][plugin_param])

    return found_params


def check_yaml_path(paths):
    paths = [os.path.abspath(p) for p in paths]
    for p in paths:
        if not os.path.isfile(p):
            raise Exception("Template file not found at %s" % p)
    return paths


def get_data_dict(paths):
    all_data_dict = {}
    yu = YamlConverter()
    for p in paths:
        yu.parameters['yaml_file'] = p
        all_data_dict.update(yu.setup(template=True))
    return all_data_dict


def get_string_result(key, data_dict, mData, res=[]):
    if '*' in key:
        for data in list(data_dict.keys()):
            res = get_string_result(
                    key.replace('*', data), data_dict, mData, res)
    else:
        res.append(mData.get(key.split('.')))
    return res


if __name__ == '__main__':
    arg = arg_parser()
    # find all Hdf5TemplateLoaders
    plugin = 'Hdf5TemplateLoader'
    param = 'yaml_file'
    paths = check_yaml_path(get_parameter_value(arg.nxsfile, plugin, param))
    data_dict = get_data_dict(paths)
    res = get_string_result(arg.key, data_dict, MetaData(data_dict))
    print(','.join(res))

    