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
import re
import sys

from savu.plugins import utils as pu

def add_package_entry(f, files_present, output, module_name):
    """Create a contents page for the files and directories contained
    in 'files'. Create links to all the plugin classes which load without
    errors
    """
    if files_present:
        # If files are present in this directory then, depending on the
        # number of nested directories, determine which section heading
        # and title to apply
        title = module_name.split('.')

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

        # For directory contents
        f.write('\n.. toctree::\n')
        # Contents display level is set to have plugin names only
        f.write('   :maxdepth: 1 \n\n')

        for fi in files_present:
            # TODO At the moment if a directory contains files, and none of
            #  their classes load correctly, the content will be blank
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


def create_plugin_documentation(files, output, module_name, savu_base_path):
    # Create template download page
    create_plugin_template_downloads(savu_base_path)

    # Only document the plugin python files
    if not os.path.exists(savu_base_path + 'doc/source/' + output):
        # Create the directory if it does not exist
        os.makedirs(savu_base_path + 'doc/source/' + output)

    for fi in files:
        file_path = module_name + '.' + fi.split('.py')[0]
        py_module_name = 'savu.' + str(file_path)
        try:
            # Load the associated class
            plugin_class = pu.load_class(py_module_name)()
            plugin_class._populate_default_parameters()
            plugin_tools = plugin_class.tools.tools_list
            if plugin_tools:
                # Create an empty rst file inside this directory where
                # the plugin tools documentation will be stored
                new_rst_file = open(savu_base_path + 'doc/source/'
                                    + output + '/' + file_path
                                    + '.rst', 'w+')
                # Populate this file
                populate_plugin_doc_files(new_rst_file, plugin_tools,
                                          file_path, plugin_class,
                                          savu_base_path)
        except Exception as e:
            print(e)


def convert_title(original_title):
    new_title = original_title.replace('_',' ').title()
    return new_title


def populate_plugin_doc_files(new_rst_file, tool_class_list, file_path,
                              plugin_class, savu_base_path):
    """Create the restructured text file containing parameter, citation
    and documentation information for the plugin_class

    :param new_rst_file: The new restructured text file which will hold all
                            of the plugin details for this plugin class
    :param tool_class_list: The list of base tool classes for this plugin
    :param file_path: Path to the plugin file
    :param plugin_class: Plugin class
    :param savu_base_path: Savu file path
    """

    title = file_path.split('.')
    # Depending on the number of nested directories, determine which section
    # heading and title to apply
    plugin_type = title[-1]
    new_rst_file.write(convert_title(plugin_type) +
      '\n#################################################################\n')

    plugin_data = plugin_class.p_dict
    plugin_citations = plugin_class.tools.get_citations()

    tool_class = tool_class_list[-1]
    if tool_class.__doc__:
        # Remove white space
        tool_doc=tool_class.__doc__.split()
        if tool_doc:
            new_rst_file.write('\nDescription'
                                   '\n--------------------------\n')
            new_rst_file.write('\n')
            new_rst_file.write(tool_class.__doc__)

        # Locate documentation file
        doc_folder = savu_base_path + 'doc/source/documentation/'
        file_str = doc_folder + title[-1] + '_doc.rst'
        inner_file_str = '/../documentation/' + title[-1] + '_doc.rst'

        if os.path.isfile(file_str):
            # If there is a documentation file
            new_rst_file.write('\n')
            new_rst_file.write('.. toctree::')
            new_rst_file.write('\n    Plugin documention and guidelines'
                               ' on use <' + inner_file_str + '>')
            new_rst_file.write('\n')

    if tool_class.define_parameters.__doc__:
        # Check define parameters exists
        new_rst_file.write('\nParameter definitions'
                           '\n--------------------------\n')
        new_rst_file.write('\n.. code-block:: yaml')
        new_rst_file.write('\n')

        if plugin_data:
            # Go through all plugin parameters
            for p_name, p_dict in plugin_data.items():
                new_rst_file.write('\n'
                       + indent_multi_line_str
                           (get_parameter_info(p_name, p_dict), 2))

        # Key to explain parameters
        new_rst_file.write('\nKey\n^^^^^^^^^^\n')
        new_rst_file.write('\n')
        new_rst_file.write('.. literalinclude:: '
                           '/../source/files_and_images/documentation/'
                           'short_parameter_key.yaml')
        new_rst_file.write('\n    :language: yaml\n')

    if plugin_citations:
        # If documentation information is present, then display it
        new_rst_file.write('\nCitations'
                           '\n--------------------------\n')

        write_citations_to_file(new_rst_file, plugin_citations)


def get_parameter_info(p_name, parameter):
    possible_keys = ['visibility', 'dtype', 'description', 'default',
                     'options', 'range', 'dependency', 'example']

    parameter_info = p_name + ':\n'
    keys_display = [k for k in parameter.keys() if k in possible_keys]
    for key in keys_display:
        val_p = parameter[key]
        if isinstance(val_p, dict):
            str_dict = print_parameter_dict(val_p, '', 2)
            parameter_info += indent(key + ': \n' + str_dict )
        elif isinstance(val_p, str):
            if no_yaml_char(val_p):
                parameter_info += indent(key + ': ' + str(val_p) + '\n')
            else:
                parameter_info += indent(key + ': "' + str(val_p) + '"\n')
        elif isinstance(val_p, type(None)):
            parameter_info += indent(key + ':\n')
        else:
            parameter_info += indent(key + ': ' + str(val_p) + '\n')

    return parameter_info


def print_parameter_dict(input_dict, parameter_info, indent_level):
    """ Create a yaml str format for the input_dict """

    for k, v in input_dict.items():
        if isinstance(v, dict):
            # Increase the indentation level for each dictionary
            indent_level += 1
            dict_str = print_parameter_dict(v, '', indent_level)
            indent_level -= 1
            parameter_info += indent(k + ': \n' + dict_str , indent_level)
        elif isinstance(v, str):
            # Check if the string contains characters which may need
            # to be surrounded by quotes
            if no_yaml_char(v):
                parameter_info += indent(k + ': ' + str(v)
                                         + '\n', indent_level)
            else:
                # Encase the string with quotation marks
                parameter_info += indent(k + ': "' + str(v)
                                         + '"\n', indent_level)
        elif isinstance(v, type(None)):
            parameter_info += indent(k + ':\n', indent_level)
        elif isinstance(v, list):
            indent_level += 1
            list_str = ''
            for item in v:
                list_str += indent( item + '\n', indent_level)
            indent_level -= 1
            parameter_info += indent(k + ': \n' + list_str, indent_level)
        else:
            parameter_info += indent(k + ': ' + str(v) + '\n', indent_level)

    return parameter_info


def no_yaml_char(s):
    """ Check for characters which prevent the yaml syntax highlighter
    from being applied. For example [] and ? and '
    """
    return bool(re.match(r'^[a-zA-Z0-9()%|#\"/._,+\-=: {}<>]*$', s))


def indent_multi_line_str(text, indent_level=1, justify=False):
    text = text.split('\n')
    # Remove additional spacing on the left side so that text aligns
    if justify is False:
        text = [(' '*4*indent_level) + line for line in text]
    else:
        text = [(' '*4*indent_level) + line.lstrip() for line in text]
    text = '\n'.join(text)
    return text


def indent(text, indent_level=1):
    text = (' '*4*indent_level) + text
    return text


def write_citations_to_file(new_rst_file, plugin_citations):
    """Create the citation text format """
    for name, citation in plugin_citations.items():
        new_rst_file.write('\n' + name.encode('utf-8').lstrip() +
                           '\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
                           '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
                           '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
                           '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        if hasattr(citation, 'dependency'):
            for k, v in citation.dependency.items():
                new_rst_file.write('\n(Please use this citation if '
                                   'you are using the '
                                   + v + ' ' + k +')\n')
        bibtex = citation.bibtex
        endnote = citation.endnote
        # Where new lines are, append an indentation
        if bibtex:
            new_rst_file.write('\nBibtex'
                               '\n""""""""""""""""""""'
                               '""""""""""""""""""""""\n')
            new_rst_file.write('\n.. code-block:: none')
            new_rst_file.write('\n\n')
            new_rst_file.write(indent_multi_line_str(bibtex, True))
            new_rst_file.write('\n')

        if endnote:
            new_rst_file.write('\nEndnote'
                               '\n""""""""""""""""""""'
                               '""""""""""""""""""""""\n')
            new_rst_file.write('\n.. code-block:: none')
            new_rst_file.write('\n\n')
            new_rst_file.write(indent_multi_line_str
                               (endnote.encode('utf-8'), True))
            new_rst_file.write('\n')

    new_rst_file.write('\n')


def create_plugin_template_downloads(savu_base_path):
    """ Inside plugin_examples/plugin_templates/general
    If the file begins with 'plugin_template' then select it
    Read the lines of the files docstring and set as a descriptor
    """
    doc_template_file = savu_base_path \
                        + 'doc/source/dev_guides/dev_plugin_templates.rst'
    plugin_ex_path = savu_base_path \
                     + 'plugin_examples/plugin_templates/general'
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

    template_file = savu_base_path \
                    + 'plugin_examples/plugin_templates/general'

    all_files = []
    for (dirpath, dirnames, filenames) in os.walk(template_file):
        all_files.extend(filenames)

    inner_file_str = '../../../' + 'plugin_examples/plugin_templates/general'
    for file in all_files:
        if file.startswith('plugin_template'):
            doc_str = file.split('.py')[0]
            doc_f.write(':download:`'+ doc_str + ' <' + inner_file_str
                        +  '/' + file + '>`')
            doc_f.write('\n\n\n')

    doc_f.close()

if __name__ == "__main__":
    out_folder, rst_file, api_type = sys.argv[1:]

    # determine Savu base path
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('doc')[0]

    # open the autosummary file
    f = open(savu_base_path + 'doc/source/' + rst_file, 'w')

    document_title = convert_title(out_folder)
    f.write('.. _' + out_folder+':\n')
    f.write('\n**********************\n' + document_title
            +' \n**********************\n\n')

    base_path = savu_base_path + 'savu/plugins'
    # create entries in the autosummary for each package

    exclude_file = ['__init__.py',
                    'parameter_utils.py', 'docstring_parser.py', 'plugin.py',
                    'plugin_datasets.py', 'plugin_datasets_notes.py',
                    'utils.py', 'plugin_tools.py', 'yaml_utils.py',
                    'hdf5_utils.py']
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
                    create_plugin_documentation(files, out_folder,
                                            module_name, savu_base_path)