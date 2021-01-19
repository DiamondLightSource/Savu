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

from collections import OrderedDict

import savu.plugins.utils as pu
import scripts.config_generator.savu_config as sc

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
            mod_path = module_name + '.' + fi.split('.py')[0]
            # Use the module path '.' file name for api documentation
            # Use the file path '/' file name for plugin documentation
            file_path = mod_path.replace('.', '/') \
                if output == 'plugin_documentation' else mod_path
            py_module_name = 'savu.' + str(mod_path)
            try:
                # If the plugin class exists, put it's name into the contents
                plugin_class = pu.load_class(py_module_name)
                name = convert_title(fi.split('.py')[0])
                f.write('   ' + name + ' <' + output + '/' + file_path + '>\n')
            except Exception:
                pass
        f.write('\n\n')


def create_plugin_documentation(files, output, module_name, savu_base_path):
    for fi in files:
        mod_path = module_name + '.' + fi.split('.py')[0]
        file_path = mod_path.replace('.', '/')
        py_module_name = 'savu.' + str(mod_path)
        try:
            # Load the associated class
            plugin_class = pu.load_class(py_module_name)()
            plugin_class._populate_default_parameters()
            try:
                plugin_tools = plugin_class.tools.tools_list
                if plugin_tools:
                    # Create rst additional documentation directory
                    # and file and image directory
                    create_documentation_directory(savu_base_path, fi)
                    # Create an empty rst file inside this directory where
                    # the plugin tools documentation will be stored
                    full_file_path = savu_base_path + 'doc/source/reference/' \
                                     + output + '/' + file_path + '.rst'
                    pu.create_dir(full_file_path)
                    with open(full_file_path, 'w+') as new_rst_file:
                        # Populate this file
                        populate_plugin_doc_files(new_rst_file, plugin_tools,
                                                  file_path, plugin_class,
                                                  savu_base_path)
            except:
                print(f'Tools file missing for {py_module_name}')
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

    title = file_path.split('/')
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
        doc_folder = savu_base_path + 'doc/source/explanation/'
        file_str = doc_folder + file_path + '_doc.rst'
        inner_file_str = '/../../../explanation/' + file_path + '_doc.rst'

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
                       + pu.indent_multi_line_str
                           (get_parameter_info(p_name, p_dict), 2))

        # Key to explain parameters
        new_rst_file.write('\nKey\n^^^^^^^^^^\n')
        new_rst_file.write('\n')
        new_rst_file.write('.. literalinclude:: '
                           '/../source/files_and_images/plugin_guides/'
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
            parameter_info += pu.indent(key + ': \n' + str_dict )
        elif isinstance(val_p, str):
            if no_yaml_char(val_p):
                parameter_info += pu.indent(key + ': ' + str(val_p) + '\n')
            else:
                parameter_info += pu.indent(key + ': "' + str(val_p) + '"\n')
        elif isinstance(val_p, type(None)):
            parameter_info += pu.indent(key + ':\n')
        else:
            parameter_info += pu.indent(key + ': ' + str(val_p) + '\n')

    return parameter_info


def print_parameter_dict(input_dict, parameter_info, indent_level):
    """ Create a yaml str format for the input_dict """

    for k, v in input_dict.items():
        if isinstance(v, dict):
            # Increase the indentation level for each dictionary
            indent_level += 1
            dict_str = print_parameter_dict(v, '', indent_level)
            indent_level -= 1
            parameter_info += pu.indent(k + ': \n' + dict_str , indent_level)
        elif isinstance(v, str):
            # Check if the string contains characters which may need
            # to be surrounded by quotes
            if no_yaml_char(v):
                parameter_info += pu.indent(k + ': ' + str(v)
                                         + '\n', indent_level)
            else:
                # Encase the string with quotation marks
                parameter_info += pu.indent(k + ': "' + str(v)
                                         + '"\n', indent_level)
        elif isinstance(v, type(None)):
            parameter_info += pu.indent(k + ':\n', indent_level)
        elif isinstance(v, list):
            indent_level += 1
            list_str = ''
            for item in v:
                list_str += pu.indent( item + '\n', indent_level)
            indent_level -= 1
            parameter_info += pu.indent(k + ': \n' + list_str, indent_level)
        else:
            parameter_info += pu.indent(k + ': ' + str(v) + '\n', indent_level)

    return parameter_info


def no_yaml_char(s):
    """ Check for characters which prevent the yaml syntax highlighter
    from being applied. For example [] and ? and '
    """
    return bool(re.match(r'^[a-zA-Z0-9()%|#\"/._,+\-=: {}<>]*$', s))


def write_citations_to_file(new_rst_file, plugin_citations):
    """Create the citation text format """
    for name, citation in plugin_citations.items():
        new_rst_file.write('\n' + name.lstrip() +
                           '\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
                           '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
                           '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
                           '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        if citation.dependency:
            # If the citation is dependent upon a certain parameter value
            # being chosen
            for citation_dependent_parameter, citation_dependent_value \
                    in citation.dependency.items():
                new_rst_file.write('\n(Please use this citation if '
                                   'you are using the '
                                   + citation_dependent_value
                                   + ' '
                                   + citation_dependent_parameter +')\n')
        bibtex = citation.bibtex
        endnote = citation.endnote
        # Where new lines are, append an indentation
        if bibtex:
            new_rst_file.write('\nBibtex'
                               '\n""""""""""""""""""""'
                               '""""""""""""""""""""""\n')
            new_rst_file.write('\n.. code-block:: none')
            new_rst_file.write('\n\n')
            new_rst_file.write(pu.indent_multi_line_str(bibtex, True))
            new_rst_file.write('\n')

        if endnote:
            new_rst_file.write('\nEndnote'
                               '\n""""""""""""""""""""'
                               '""""""""""""""""""""""\n')
            new_rst_file.write('\n.. code-block:: none')
            new_rst_file.write('\n\n')
            new_rst_file.write(pu.indent_multi_line_str
                               (endnote, True))
            new_rst_file.write('\n')

    new_rst_file.write('\n')


def create_plugin_template_downloads(savu_base_path):
    """ Inside plugin_examples/plugin_templates/general
    If the file begins with 'plugin_template' then select it
    Read the lines of the files docstring and set as a descriptor
    """
    doc_template_file = savu_base_path \
                        + 'doc/source/dev_guides/dev_plugin_templates.rst'
    # Populate dictionary with template class and template class docstring
    docstring_text = create_template_class_dict(savu_base_path)
    if docstring_text:
        with open(doc_template_file, 'w') as doc_template:
            doc_template.write('.. _plugin_templates:\n')
            doc_template.write('\n')
            doc_template.write('Plugin templates \n=======================\n')
            doc_template.write('\n')

            doc_name = 'plugin_template1_with_detailed_notes'
            detailed_template = docstring_text.get(doc_name)

            if detailed_template:
                docstring_text.pop(doc_name)
                title = convert_title(doc_name)
                title, number = filter_template_numbers(title)
                # Create the restructured text page for the plugin template
                # python code
                generate_template_files(doc_name, title)
                inner_file_str = '../../../' + 'plugin_examples/plugin_templates/general'
                doc_text = detailed_template['docstring'].split(':param')[0]
                doc_text = " ".join(doc_text.splitlines())
                doc_template.write(title
                            + '\n--------------------------------'
                              '----------------------------------\n')
                doc_template.write('\nA template to create a simple plugin '
                                   'that takes one dataset as input and returns '
                                   'a similar dataset as output')
                doc_template.write('\n')
                doc_template.write('''
.. list-table::  
   :widths: 10
   
   * - :ref:`'''+doc_name+'''`

''')
            doc_template.write('Further Examples'
                        + '\n--------------------------------'
                          '----------------------------------\n')
            # Begin the table layout
            doc_template.write('''
.. list-table::  
   :widths: 10 90
   :header-rows: 1

   * - Link
     - Description''')

            for doc_name, doc_str in docstring_text.items():
                title = convert_title(doc_name)
                title, number = filter_template_numbers(title)
                # Remove the parameter information from the docstring
                doc_text = doc_str['docstring'].split(':param')[0]
                doc_text = " ".join(doc_text.splitlines())
                # Create a link to the restructured text page view of the python
                # code for the template
                doc_template.write('\n   * - :ref:`'+doc_name+'`')
                # The template description from the docstring
                doc_template.write('\n     - '+doc_text)
                doc_template.write('\n')
                # Create the restructured text page for the plugin template
                # python code
                generate_template_files(doc_name, title)

            doc_template.write('\n')


def generate_template_files(doc_name, title):
    """ Create a restructured text file which will inclide the python
     code for the plugin template 'doc_name'

    :param doc_name: The name of the template file
    :param title:
    :return:
    """
    inner_file_str = '../../../../' + 'plugin_examples/plugin_templates/general'
    template_file_path = savu_base_path \
                        + 'doc/source/dev_guides/templates/'\
                         + doc_name + '.rst'
    with open(template_file_path, 'w') as template_file:
        # Add the orphan instruction as this file is not inside a toctree
        template_file.write(':orphan:\n')
        template_file.write('\n.. _' + doc_name + ':\n')
        template_file.write('\n')
        template_file.write(title+'\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
        template_file.write('\n')
        template_file.write(':download:`Download <' + inner_file_str
                    + '/' + doc_name + '.py>`\n\n')
        template_file.write('\n')
        template_file.write('.. literalinclude:: '
                           '/../../plugin_examples/plugin_templates/general/'
                            + doc_name + '.py')
        template_file.write('\n    :language: python\n')


def filter_template_numbers(name_string):
    """
    :param name_string: The name of the template
    :return: A string with the template number seperated by a space
    """
    number = ''.join(l for l in name_string if l.isdigit())
    letters = ''.join(l for l in name_string if l.isalpha())
    split_uppercase = [l for l in re.split("([A-Z][^A-Z]*)", letters) if l]
    title = ' '.join(split_uppercase)
    name = title + ' ' + number
    return name, number

def create_template_class_dict(savu_base_path):
    """ Iterate through the plugin example folder and store the class
    and it's class docstring into a dictionary docstring_text

    :param savu_base_path:
    :return: docstring_text dictionary of class and docstring
    """
    docstring_text = {}
    plugin_ex_path = savu_base_path \
                     + 'plugin_examples/plugin_templates/general'

    for t_root, t_dirs, template_files \
            in os.walk(plugin_ex_path, topdown=True):
        template_files[:] = [fi for fi in template_files
                             if fi.split('.')[-1] == 'py']
        if '__' not in t_root:
            pkg_path = t_root.split('Savu/')[1]
            module_name = pkg_path.replace('/', '.')

        for fi in template_files:
            file_name = fi.split('.py')[0]
            cls_module = module_name + '.' + file_name
            try:
                cls_loaded = pu.load_class(cls_module)
            except:
                cls_loaded = None

            if cls_loaded:
                title = convert_title(file_name)
                name, number = filter_template_numbers(title)
                docstring_text[file_name] = \
                    {'docstring': cls_loaded.__doc__, 'number': int(number)}

    # Order templates by number
    docstring_text = OrderedDict(sorted(docstring_text.items(),
                                        key=lambda i: i[1]['number']))

    return docstring_text


def create_savu_config_documentation(savu_base_path):
    """ Look at the available commands inside savu_config
    Create a rst text file for each.
    """
    command_file_path = savu_base_path \
                        + 'doc/source/reference/savu_config_commands.rst'
    with open(command_file_path, 'w') as command_file:
        savu_command_test_start = '''
Savu Config Commands
**********************

The links on this page provide help for each command.
If you are using the command line please type ``-h`` or ``--help``.

.. code-block:: bash

   savu_config --help

'''
        # Write contents
        command_file.write(savu_command_test_start)
        for command in sc.commands:
            command_file.write('\n')
            command_file.write('* :ref:`' + command + '`')
            command_file.write('\n')

        # Document commands
        for command in sc.commands:
            command_file.write('\n')
            command_file.write('.. _'+command+':')
            command_file.write('\n\n'+command)
            command_file.write('\n--------------')
            command_file.write('\n')
            command_file.write('\n.. cssclass:: argstyle')
            command_file.write('\n    .. argparse::')
            command_file.write('\n            :module: scripts.config_generator.arg_parsers')
            command_file.write('\n            :func: _'+command+'_arg_parser')
            command_file.write('\n            :prog: '+command)
            command_file.write('\n')
            command_file.write('\n')


def create_documentation_directory(savu_base_path, plugin_file):
    """ Create plugin directory inside documentation and
    documentation file and image folders
    """
    # Create directory inside
    doc_path = savu_base_path \
               + 'doc/source/explanation/'
    doc_image_path = savu_base_path \
        + 'doc/source/files_and_images/plugin_guides/plugins/'

    # find the directories to create
    doc_dir = doc_path + plugin_file
    image_dir = doc_image_path + plugin_file
    pu.create_dir(doc_dir)
    pu.create_dir(image_dir)


if __name__ == "__main__":
    out_folder, rst_file, api_type = sys.argv[1:]

    # determine Savu base path
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('doc')[0]

    base_path = savu_base_path + 'savu/plugins'
    # create entries in the autosummary for each package

    exclude_file = ['__init__.py',
                    'parameter_utils.py', 'docstring_parser.py', 'plugin.py',
                    'plugin_datasets.py', 'plugin_datasets_notes.py',
                    'utils.py', 'plugin_tools.py', 'yaml_utils.py',
                    'hdf5_utils.py']
    exclude_dir = ['driver']

    # Create template download page
    create_plugin_template_downloads(savu_base_path)

    # Create savu_config command rst files
    # create_config_documentation(savu_base_path)
    create_savu_config_documentation(savu_base_path)

    # Only document the plugin python files
    # Create the directory if it does not exist
    pu.create_dir(savu_base_path + 'doc/source/reference/' + out_folder)

    # open the autosummary file
    with open(savu_base_path + 'doc/source/reference/' + rst_file, 'w') as f:

        document_title = convert_title(out_folder)
        f.write('.. _' + out_folder+':\n')
        f.write('\n**********************\n' + document_title
                +' \n**********************\n\n')

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