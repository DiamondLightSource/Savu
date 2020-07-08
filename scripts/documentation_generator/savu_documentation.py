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
.. module:: savu_documentation
   :platform: Unix
   :synopsis: A command line tool for creating Savu plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

#from __future__ import print_function, division

import re, os
import sys
import argparse

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from scripts.config_generator.content import Content
    from savu.plugins import utils as pu
    from scripts.config_generator import config_utils as utils

def __option_parser():
    """ Option parser for command line arguments.
    """
    parser = argparse.ArgumentParser(prog='savu_documentation')
    parser.add_argument('plugin_name', help='Plugin name to create file', nargs= '+')
    return parser.parse_args()

def get_plugin_class(plugin_name):
    # Return the class for the given plugin
    plugins = Content()
    utils.populate_plugins()
    if plugin_name not in pu.plugins.keys():
        print('The plugin named %s is not in the list of registered plugins.' % plugin_name)
        plugin_class = None
    else:
        plugin_class = pu.plugins[plugin_name]()
    return plugin_class

def append_file(f,openfile):# adds openfile onto main file f
    with open(openfile) as input:
        f.write(input.read())
        input.close

def create_plugin_template(file_path, module):
    # Locate python file
    savu_base_path = os.path.abspath('../../')
    plugin_folder = savu_base_path + '/' + file_path
    title = module.split('.')
    capital_title = title[-1].title().replace('_', '')
    file_str = plugin_folder  +'.py'

    if os.path.isfile(file_str):
        # Get the link
        print('A plugin file exists at ' + file_str)
    else:
        with open(file_str, 'w+') as new_py_file:
            append_file(new_py_file, 'template_elements/copyright.py')
            new_py_file.write(get_module_info(title[-1]).strip())
            new_py_file.write('\n')
            new_py_file.write('from savu.plugins.utils import register_plugin\n')
            new_py_file.write('from savu.plugins.plugin import Plugin\n')
            new_py_file.write('# Import any additional libraries or base plugins here.\n')
            new_py_file.write('\n')
            new_py_file.write('@register_plugin')
            new_py_file.write('\nclass ' + capital_title + '(Plugin):\n')
            new_py_file.write('\n    def __init__(self):')
            new_py_file.write('\n        super(' + capital_title)
            new_py_file.write(', self).__init__("' + capital_title + '")\n\n')
            append_file(new_py_file, 'template_elements/process_and_setup.py')

        new_py_file.close()
        print('A plugin file has been created at ' + file_str)


def create_tools_template(file_path, module):
    # Locate tools file
    savu_base_path = os.path.abspath('../../')
    plugin_folder = savu_base_path + '/' + file_path
    title = module.split('.')
    capital_title = title[-1].title().replace('_', '')
    file_str = plugin_folder  +'_tools.py'

    if os.path.isfile(file_str):
        print('A tools file exists at ' + file_str)
    else:
        with open(file_str, 'w+') as new_tools_file:
            new_tools_file.write('from savu.plugins.plugin_tools import PluginTools\n')
            new_tools_file.write('\n')
            new_tools_file.write('class '+ capital_title + 'Tools(PluginTools):')
            new_tools_file.write('\n')
            new_tools_file.write('    """A short description of the plugin"""\n')
            new_tools_file.write('\n')
            append_file(new_tools_file, 'template_elements/parameter_definition.py')

        new_tools_file.close()
        print('A tools file has been created at ' + file_str)

def create_documentation_template(file_path, module):
    # Locate documentation file
    savu_base_path = os.path.abspath('../../')
    doc_folder = savu_base_path + '/doc/source/documentation/'
    title = module.split('.')
    file_str = doc_folder + title[-1] + '_doc.rst'

    if os.path.isfile(file_str):
        print('A documentation file exists at ' + file_str)
    else:
        with open(file_str, 'w+') as new_rst_file:
            new_rst_file.write(convert_title(title[-1]) + ' Documentation' +
                               '\n##########################################'
                               '#######################\n')
            new_rst_file.write('\n')
            new_rst_file.write('Include your plugin documentation here. Use'
                               ' a restructured text format.')
            new_rst_file.write('\n')

        new_rst_file.close()
        print('A documentation file has been created at ' + file_str)

def get_module_info(title):
    module_info =\
    '''
"""
.. module:: ''' + title + \
'''
   :platform: Unix
   :synopsis: A short description of your plugin.

.. moduleauthor:: Name of Author <email_address>
"""
    '''
    return module_info

def convert_title(original_title):
    new_title = original_title.title().replace('_', ' ')
    return new_title

def main():
    args = __option_parser()
    print("Checking if this plugin already exists..")
    plugin_name = "".join(args.plugin_name)
    plugin = get_plugin_class(plugin_name)
    if plugin == None:
        plugin_module_name =  "_".join(args.plugin_name).lower()
        module = 'savu.plugins.' + plugin_module_name
    else:
        module = plugin.__module__

    file_path = module.replace('.', '/')

    create_plugin_template(file_path, module)
    create_tools_template(file_path, module)
    create_documentation_template(file_path, module)

if __name__ == '__main__':
    main()
