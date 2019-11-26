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
.. module:: yaml_utils
   :platform: Unix
   :synopsis: Utilities for yaml files

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import yaml
from collections import OrderedDict


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    # 'Load all' is used so that multiple yaml documents may be appended with --- and read in also
    return yaml.load_all(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def read_yaml(path):
    try:
        with open(path, 'r') as stream:
            data_dict = ordered_load(stream, yaml.SafeLoader)
            return [data for data in data_dict]
    except yaml.YAMLError as e:
        print('Error reading the yaml structure with YamlLoader.')
        raise


def read_yaml_from_doc(docstring):
    """
    Take the docstring and use ordered_loading to read in the yaml format as an ordered dict.
    ----------
    Parameters:
            - docstring: String of information.
    ----------
    Return:
            - data_dict: Generator with ordered dictionaries for each yaml document.
    """
    try:
        # SafeLoader loads a subset of the YAML language, safely. This is recommended for loading untrusted input
        data_dict = ordered_load(docstring, yaml.SafeLoader)
        return data_dict
    except yaml.YAMLError as e:
        print('Error reading the yaml structure with YamlLoader.')
        raise


def dump_yaml(template, stream):
    ordered_dump(template, stream=stream, Dumper=yaml.SafeDumper,
                 default_flow_style=False)
