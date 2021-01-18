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
.. module:: parameter_extractor
   :platform: Unix
   :synopsis: Extract parameter values

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import argparse

from scripts.config_generator.content import Content


def arg_parser(doc=True):
    """ Arg parser for command line arguments.
    """
    parser = argparse.ArgumentParser(prog='update_template')
    parser.add_argument('nxsfile', help='The nexus file')
    parser.add_argument('plugin', help='Plugin name')
    parser.add_argument('param', help='plugin parameter name')
    return parser if doc == True else parser.parse_args()

def get_parameter_value(nxsfile, plugin_name, plugin_param):
    content = Content()
    content.fopen(nxsfile)
    plist = content.plugin_list.plugin_list
    
    for plugin in plist:
        if plugin['name'] == plugin_name:
            if plugin_param in list(plugin['data'].keys()):
                print(plugin_name, plugin['data'][plugin_param])

if __name__ == '__main__':
    arg = arg_parser(doc=False)
    get_parameter_value(arg.nxsfile, arg.plugin, arg.param)
