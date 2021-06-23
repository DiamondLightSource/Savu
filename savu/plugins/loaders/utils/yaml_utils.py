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
import sys
import savu
import yaml
import traceback

from yamllint import linter
from collections import OrderedDict
from yamllint.config import YamlLintConfig

from savu.plugins.loaders.utils.my_safe_constructor import MySafeConstructor

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader, MySafeConstructor):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            list(data.items()))
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    
    def represent_none(self, _):
        return self.represent_scalar('tag:yaml.org,2002:null', '')
    OrderedDumper.add_representer(type(None), represent_none)
    
    return yaml.dump(data, stream, OrderedDumper, **kwds)

def check_yaml_errors(data):
    config_file = savu.__path__[0] + '/plugins/loaders/utils/yaml_config.yaml'
    with open(config_file) as config_file_data:
        conf = YamlLintConfig(config_file_data)
        gen = linter.run(data, conf)
        errors = list(gen)
    return errors

def read_yaml(path):
    with open(path, 'r') as stream:
        data_dict = ordered_load(stream, yaml.SafeLoader)
    return data_dict

def read_yaml_from_doc(docstring):
    """Take the docstring and use ordered_loading to read in the yaml format as an ordered dict.

    Parameters
    -----------
    docstring : str
        String of information.

    Returns
    -------
    data_dict : dict
        Generator with ordered dictionaries for each yaml document.

    """
    errors = check_yaml_errors(docstring)
    try:
        # SafeLoader loads a subset of the YAML language, safely.
        # This is recommended for loading untrusted input
        data_dict = ordered_load(docstring, yaml.SafeLoader)
        return data_dict
    except (yaml.scanner.ScannerError, yaml.parser.ParserError) as se:
        print('')
        for e in errors:
            print(e)
        raise
    except yaml.YAMLError as ye:
        print("Error reading the yaml structure with YamlLoader.")
        raise Exception(sys.exc_info())

def dump_yaml(template, stream):
    ordered_dump(template, stream=stream, Dumper=yaml.SafeDumper,
                 default_flow_style=False)

