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

def add_package_entry(f, files, output, module_name):
    plugin_class = None
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
    # Contents display level is set to have plugin names only
    f.write('   :maxdepth: 1 \n\n')
    for fi in files:
        file_path = module_name + '.' + fi.split('.py')[0]
        py_module_name = 'savu.' + str(file_path)
        try:
            # If the plugin class exists, put it's name into the contents
            plugin_class = pu.load_class(py_module_name)
            name = convert_title(fi.split('.py')[0])
            f.write('   ' + name + ' <' + output + '/' + file_path + '>\n')
        except Exception:
            pass
    f.write('\n\n')

def create_plugin_documentation(files, output, module_name):
    savu_base_path = os.path.abspath('../')
    # Only document the plugin python files
    if not os.path.exists(savu_base_path + '/doc/source/' + output):
        # Create the directory if it does not exist
        os.makedirs(savu_base_path + '/doc/source/' + output)

    for fi in files:
        file_path = module_name + '.' + fi.split('.py')[0]
        py_module_name = 'savu.' + str(file_path)
        try:
            # Load the associated class
            plugin_class = pu.load_class(py_module_name)
            p_tools_list =[]
            # Using method resolution order, find base class tools
            for clazz in plugin_class.__mro__[::-1]:
                py_module_name = clazz.__module__ + '_tools'
                p_tools = pu.get_tools_class(py_module_name)
                if p_tools and p_tools!= 'plugins.plugin_tools':
                    p_tools_list.append(p_tools)

            if p_tools_list:
                # Create an empty rst file inside this directory where
                # the plugin tools documentation will be stored
                new_rst_file = open(savu_base_path + '/doc/source/'
                                    + output + '/' + file_path
                                    + '.rst', 'w+')
                # Populate this file
                populate_plugin_doc_files(new_rst_file, p_tools_list, file_path, plugin_class)
        except Exception as e:
            print(e)

def convert_title(original_title):
    new_title = original_title.replace('_',' ').title()
    return new_title

def populate_plugin_doc_files(new_rst_file, tool_class_list, file_path, plugin_class):
    title = file_path.split('.')
    # Depending on the number of nested directories, determine which section
    # heading and title to apply
    plugin_type = title[-1]
    new_rst_file.write(convert_title(plugin_type) +
      '\n#################################################################\n')

    # Populate the class and display the parameter detail
    p = plugin_class()
    p._populate_default_parameters()
    plugin_data = p.p_dict
    plugin_citations = p.tools.get_citations()

    tool_class = tool_class_list[-1]
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

        for bases_tool_class in tool_class_list:
            plugin_parameters = bases_tool_class.define_parameters.__doc__
            if plugin_parameters:
                # Go through all plugin classes and get the function and docstring
                new_rst_file.write('\n    ' + plugin_parameters)
                # TODO Append the tools parameters

        # Key to explain parameters
        new_rst_file.write('\nKey\n^^^^^^^^^^\n')
        new_rst_file.write('\n')
        new_rst_file.write('.. literalinclude:: '
                           '/../source/files_and_images/documentation/short_parameter_key.yaml')
        new_rst_file.write('\n    :language: yaml\n')

    # Locate documentation file
    savu_base_path = os.path.abspath('../')
    doc_folder = savu_base_path + '/doc/source/documentation/'
    file_str = doc_folder + title[-1] + '_doc.rst'
    inner_file_str = '/../documentation/' + title[-1] + '_doc.rst'

    if os.path.isfile(file_str) \
            or plugin_citations:
        # If documentation information is present, then display it
        new_rst_file.write('\nDocumentation'
                           '\n--------------------------\n')

        if os.path.isfile(file_str):
            # If there is a documentation file
            new_rst_file.write('\n')
            new_rst_file.write('.. toctree::')
            new_rst_file.write('\n    Plugin documention and guidelines on use <'
                               + inner_file_str + '>')
            new_rst_file.write('\n')

        if plugin_citations:
            new_rst_file.write('\nCitations'
                               '\n^^^^^^^^^^^^^^^^^^^^^^^^\n')

            for name, citation in plugin_citations.items():
                new_rst_file.write('\n' + name.encode('utf-8').lstrip() +
                '\n""""""""""""""""""""""""""""""""""""""""""""""'
                '""""""""""""""""""""""""""""""""""""""""""""""""'
                '""""""""""""""""""""""""""""""""""""""""""""""""'
                '""""""""""""""""""""""""""""""""""""""""""""""""\n\n')
                new_rst_file.write(citation.description)
                new_rst_file.write('\n')

                bibtex = citation.bibtex
                endnote = citation.endnote
                # Where new lines are, append an indentation
                if bibtex:
                    new_rst_file.write('\nBibtex'
                    '\n````````````````````````````````````````````````\n')
                    new_rst_file.write('\n.. code-block:: none')
                    new_rst_file.write('\n\n')
                    new_rst_file.write(_indent(bibtex))
                    new_rst_file.write('\n')

                if endnote:
                    new_rst_file.write('\nEndnote'
                    '\n````````````````````````````````````````````````\n')
                    new_rst_file.write('\n.. code-block:: none')
                    new_rst_file.write('\n\n')
                    new_rst_file.write(_indent(endnote.encode('utf-8')))
                    new_rst_file.write('\n')

            new_rst_file.write('\n')

def _indent(text):
    text = text.split('\n')
    # Remove additional spacing on the left side so that text aligns
    text = [('    ') + line.lstrip() for line in text]
    text = '\n'.join(text)
    return text


def create_plugin_template_downloads():
    """ Inside plugin_examples/plugin_templates/general
    If the file begins with 'plugin_template' then select it
    Read the lines of the files docstring and set as a descriptor
    """

    savu_base_path = os.path.abspath('../')
    doc_template_file = savu_base_path + '/doc/source/dev_guides/dev_plugin_templates.rst'

    plugin_ex_path = savu_base_path + '/plugin_examples/plugin_templates/general'
    # create entries in the autosummary for each package

    for root, dirs, files in os.walk(plugin_ex_path, topdown=True):
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
        if '__' not in root:
            pkg_path = root.split('Savu/')[1]
            module_name = pkg_path.replace('/', '.')

    for fi in files:
        cls_module ='savu.'+ module_name +'.'+ fi.split('.py')[0]
        # TODO Display the template docstrings
        # import plugin_examples.plugin_templates.general.plugin_template1 as pt1
        # print(cls_module)
        # importlib.import_module(cls_module)
        # cls_loaded = pu.load_class(cls_module)

    # open the autosummary file
    doc_f = open(doc_template_file, 'w')

    # add header
    doc_f.write('.. _plugin_templates:\n')
    doc_f.write('\n')

    doc_f.write('Plugin templates \n=======================\n')
    doc_f.write('\n')

    template_file = savu_base_path + '/plugin_examples/plugin_templates/general'

    all_files = []
    for (dirpath, dirnames, filenames) in os.walk(template_file):
        all_files.extend(filenames)

    inner_file_str = '../../../' + 'plugin_examples/plugin_templates/general'
    for file in all_files:
        if file.startswith('plugin_template'):
            doc_str = file.split('.py')[0]
            doc_f.write(':download:`'+ doc_str + ' <' + inner_file_str +  '/' + file
                + '>`')
            doc_f.write('\n\n\n')

    doc_f.close()

if __name__ == "__main__":
    out_folder, rst_file, api_type = sys.argv[1:]

    # determine Savu base path
    savu_base_path = os.path.abspath('../')

    create_plugin_template_downloads()

    # open the autosummary file
    f = open(savu_base_path + '/doc/source/' + rst_file, 'w')

    document_title = convert_title(out_folder)
    f.write('.. _' + out_folder+':\n')
    f.write('\n**********************\n' + document_title
            +' \n**********************\n')

    base_path = savu_base_path + '/savu/plugins'
    # create entries in the autosummary for each package

    exclude_file = ['__init__.py',
                    'parameter_utils.py', 'docstring_parser.py', 'plugin.py',
                    'plugin_datasets.py', 'plugin_datasets_notes.py','utils.py',
                    'plugin_tools.py', 'yaml_utils.py', 'hdf5_utils.py']
    exclude_dir = ['driver']

    for root, dirs, files in os.walk(base_path, topdown=True):
        tools_files = [fi for fi in files if 'tools' in fi]
        base_files = [fi for fi in files if fi.startswith('base')]
        driver_files = [fi for fi in files if 'driver' in fi]
        dirs[:] = [d for d in dirs if d not in exclude_dir]
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
        files[:] = [fi for fi in files if fi not in exclude_file]
        files[:] = [fi for fi in files if fi not in tools_files]
        files[:] = [fi for fi in files if fi not in base_files]
        files[:] = [fi for fi in files if fi not in driver_files]
        # Exclude the tools files fron html view sidebar
        if '__' not in root:
            pkg_path = root.split('Savu/')[1]
            module_name = pkg_path.replace('/', '.')
            module_name = module_name.replace('savu.', '')
            if 'plugins' in module_name:
                add_package_entry(f, files, out_folder, module_name)
                if out_folder == 'plugin_documentation':
                    create_plugin_documentation(files, out_folder, module_name)