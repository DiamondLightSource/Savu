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
.. module:: create_plugin_doc
   :platform: Unix
   :synopsis: A module to automatically create plugin documentation

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import sys
from savu.plugins import utils as pu

def list_of_packages(base_path):
    pkg_list = []
    for entry in os.listdir(base_path):
        entry_path = os.path.join(base_path, entry)
        if not os.path.isfile(entry_path):
            pkg_list.append(entry_path)
    return pkg_list

def add_package_entry(f, files, output, module_name):
    title = module_name.split('.')
    # Depending on the number of nested directories, determine which
    # section heading and title to apply
    if len(title) == 2:
        plugin_type = title[1]
        f.write(convert_title(plugin_type) +
          '\n########################################################\n')

    elif len(title) == 3:
        plugin_type = title[2]
        f.write(convert_title(plugin_type) +
                '\n********************************************************\n')

    elif len(title) == 4:
        plugin_type = title[3]
        f.write(convert_title(plugin_type) +
                '\n--------------------------------------------------------\n')

    f.write('\n.. toctree::\n')
    for fi in files:
        file_path = module_name + '.' + fi.split('.py')[0]
        name = convert_title(fi.split('.py')[0])
        f.write('   '+ name + ' <' + output + '/' + file_path +'>\n')
    f.write('\n\n')

def create_plugin_documentation(files, output, module_name):
    savu_base_path = os.path.abspath('../')
    # Only document the plugin python files
    if not os.path.exists(savu_base_path + '/doc/source/' + output):
        # Create the directory if it does not exist
        os.makedirs(savu_base_path + '/doc/source/' + output)

    for fi in files:
        file_path = module_name + '.' + fi.split('.py')[0]
        tools_module_name = 'savu.' + str(file_path) + '_tools'

        try:
            tool_class = pu.get_tools_class(tools_module_name)
            # Create an empty rst file inside this directory where
            # the plugin tools documentation will be stored
            if tool_class and tool_class!= 'plugins.plugin_tools':
                new_rst_file = open(savu_base_path + '/doc/source/'
                                    + output + '/' + file_path
                                    + '.rst', 'w+')
                # Populate this file
                populate_plugin_doc_files(new_rst_file, tool_class, file_path)

        except Exception as e:
            print(e)

def convert_title(original_title):
    new_title = original_title.replace('_',' ').title()
    return new_title

def populate_plugin_doc_files(new_rst_file, tool_class, file_path):
    title = file_path.split('.')
    # Depending on the number of nested directories, determine which section
    # heading and title to apply
    plugin_type = title[-1]
    new_rst_file.write(convert_title(plugin_type) +
      '\n#################################################################\n')

    if tool_class.__doc__:
        new_rst_file.write('\nDescription'
                               '\n--------------------------\n')
        new_rst_file.write('\n')
        new_rst_file.write(tool_class.__doc__)

    if tool_class.define_parameters.__doc__:
        # Check define parameters exists
        new_rst_file.write('\nParameter definitions'
                           '\n--------------------------\n')
        new_rst_file.write('\n.. code-block:: yaml')
        new_rst_file.write('\n')

        # Go through all plugin classes and get the function and docstring
        new_rst_file.write('\n    '
                           + tool_class.define_parameters.__doc__)

        # Key to explain parameters
        new_rst_file.write('\nKey\n^^^^^^^^^^\n')
        new_rst_file.write('\n')
        new_rst_file.write('.. literalinclude:: '
                           '/../source/documentation/short_parameter_key.yaml')
        new_rst_file.write('\n    :language: yaml\n')

    # Locate documentation file
    savu_base_path = os.path.abspath('../')
    doc_folder = savu_base_path + '/doc/source/documentation/'
    file_str = doc_folder + title[-1] + '_doc.rst'
    inner_file_str = '/../documentation/' + title[-1] + '_doc.rst'

    bibtex = tool_class.get_bibtex.__doc__
    endnote = tool_class.get_endnote.__doc__

    if os.path.isfile(file_str) or bibtex or endnote:
        # If documentation present then dispay it
        new_rst_file.write('\nDocumentation'
                           '\n--------------------------\n')

        if os.path.isfile(file_str):
            new_rst_file.write('\n')
            new_rst_file.write('.. toctree::')
            new_rst_file.write('\n    Plugin documention and guidelines on use <'
                               + inner_file_str + '>')
            new_rst_file.write('\n')

        if bibtex:
            new_rst_file.write('\nBibtex\n^^^^^^^^^^^^^^^^^^\n')
            new_rst_file.write('\n.. code-block:: none')
            new_rst_file.write('\n')
            new_rst_file.write('\n    '+ bibtex)
            new_rst_file.write('\n')

        if endnote:
            new_rst_file.write('\nEndnote\n^^^^^^^^^^^^^^^^^^^^\n')
            new_rst_file.write('\n.. code-block:: none')
            new_rst_file.write('\n')
            new_rst_file.write('\n    ' + endnote)
            new_rst_file.write('\n')

        new_rst_file.write('\n')

if __name__ == "__main__":
    out_folder, rst_file, api_type = sys.argv[1:]

    # determine Savu base path
    savu_base_path = os.path.abspath('../')

    # open the autosummary file
    f = open(savu_base_path + '/doc/source/' + rst_file, 'w')

    document_title = convert_title(out_folder)
    f.write('.. _' + out_folder+':\n')
    f.write('\n**********************\n' + document_title
            +' \n**********************\n')
    exclude_dir = ['__pycache__', 'test', 'core', 'data']

    base_path = savu_base_path + '/savu'
    # create entries in the autosummary for each package

    exclude_file = ['__init__.py', 'tomo_recon.py', 'version.py',
                    'parameter_utils.py', 'docstring_parser.py', 'plugin.py',
                    'plugin_datasets.py', 'plugin_datasets_notes.py','utils.py',
                    'plugin_tools.py']

    for root, dirs, files in os.walk(base_path, topdown=True):
        tools_files = [fi for fi in files if 'tools' in fi]
        dirs[:] = [d for d in dirs if d not in exclude_dir]
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
        files[:] = [fi for fi in files if fi not in exclude_file]
        files[:] = [fi for fi in files if fi not in tools_files]
        # Exclude the tools files fron html view sidebar
        if '__' not in root:
            pkg_path = root.split('Savu/')[1]
            module_name = pkg_path.replace('/', '.')
            module_name = module_name.replace('savu.', '')
            if 'plugins' in module_name:
                add_package_entry(f, files, out_folder, module_name)
                if out_folder == 'plugin_documentation':
                    create_plugin_documentation(files, out_folder, module_name)