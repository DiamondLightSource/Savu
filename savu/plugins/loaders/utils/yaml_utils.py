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


def read_yaml(path):
    with open(path, 'r') as stream:
        data_dict = ordered_load(stream, yaml.SafeLoader)
    return data_dict


def dump_yaml(template, stream):
    ordered_dump(template, stream=stream, Dumper=yaml.SafeDumper,
                 default_flow_style=False)

