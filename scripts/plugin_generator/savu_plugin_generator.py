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
.. module:: savu_plugin_generator
   :platform: Unix
   :synopsis: A command line tool for creating Savu plugins

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""

import os
import string
import argparse

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from savu.plugins import utils as pu
    from scripts.config_generator import config_utils as utils


def __option_parser(doc=True):
    """Option parser for command line arguments. Use -d for file deletion
    and -q for quick template.
    """
    desc = (
        "Generate three plugin files: a plugin file, a plugin tools "
        "file and a plugin guide file. These files will be stored inside "
        "the Savu directory and the file paths will be printed to the screen."
    )
    parser = argparse.ArgumentParser(
        prog="savu_plugin_generator", description=desc
    )
    plugin_name_help = (
        "Plugin name to create file. \n If you would like to create a plugin "
        "in a sub-folder of the 'savu/plugins' folder, e.g "
        "'savu/plugins/corrections', please add the sub-folder name like "
        "this 'corrections/plugin_name'."
    )
    parser.add_argument("plugin_name", help=plugin_name_help, type=str)
    delete_str = (
        "Delete the plugin file and its tools " "and documentation files."
    )
    parser.add_argument(
        "-q",
        "--quick",
        action="store_true",
        default="False",
        help="Create a short template version",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        default="False",
        help=delete_str,
    )
    return parser if doc is True else parser.parse_args()


def get_plugin_class(plugin_name):
    """Return the class for the given plugin"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        failed_plugins = utils.populate_plugins()

    if (failed_plugins is not None) and (
        plugin_name in failed_plugins.keys()
    ):
        print(
            f"IMPORT ERROR: {plugin_name} is unavailable due to the "
            f"following error:\n\t {failed_plugins[plugin_name]}"
        )
        # At the moment a new file is then created in the general folder.
        # A yes or no confirmation should be provided before that is created
        plugin_class = None
    elif plugin_name not in pu.plugins.keys():
        print(f"The plugin named {plugin_name} is not in the list "
              f"of registered plugins.\n")
        plugin_class = None
    else:
        plugin_class = pu.plugins[plugin_name]()
    return plugin_class


def append_file(f, additional_file):
    """ Append the additional_file on to main file f """
    with open(additional_file) as input:
        f.write(input.read())


def create_plugin_template(file_path, module, quick_arg, savu_base_path):
    """
    Find the file path for the selected plugin. Generate template files
    for those which are not present already.

    :param file_path: File path to the new file
    :param module: The module name of the new plugin
    :param quick_arg: bool True if the user wants a quick template
    :param savu_base_path: The base directory

    """
    plugin_folder = savu_base_path + file_path
    title = module.split(".")
    capital_title = convert_title(title[-1]).replace(" ", "")
    file_str = plugin_folder + ".py"
    generator_dir = savu_base_path + "scripts/plugin_generator/"
    copyright_template = generator_dir + "template_elements/copyright.py"
    detailed_template = (
        generator_dir
        + "template_elements/process_and_setup_detailed_notes.py"
    )
    quick_template = generator_dir + "template_elements/process_and_setup.py"
    if os.path.isfile(file_str):
        print("\nA plugin file exists at", file_str)
    else:
        with open(file_str, "w+") as new_py_file:
            append_file(new_py_file, copyright_template)
            new_py_file.write(get_module_info(title[-1]).strip())
            new_py_file.write('\n')
            new_py_file.write('from savu.plugins.utils '
                                            'import register_plugin\n')
            new_py_file.write('from savu.plugins.plugin import Plugin\n')
            new_py_file.write('# Import any additional libraries or base '
                              'plugins here.\n')
            new_py_file.write('\n')
            new_py_file.write('# This decorator is required for the '
                              'configurator to recognise the plugin\n')
            new_py_file.write('@register_plugin')
            new_py_file.write('\nclass ' + capital_title + '(Plugin):\n')
            new_py_file.write('# Each class must inherit from the '
                              'Plugin class and a driver\n')
            new_py_file.write('\n    def __init__(self):')
            new_py_file.write('\n        super(' + capital_title)
            new_py_file.write(', self).__init__("' + capital_title + '")\n\n')

            if quick_arg is True:
                # Concise template for previous users
                append_file(new_py_file, quick_template)
            else:
                # Detailed template for new users
                append_file(new_py_file, detailed_template)

        print("A plugin file has been created at:\n", file_str)


def create_tools_template(file_path, module, savu_base_path):
    """Locate a tools file if it exists, otherwise create a new file.
    Include a brief guide for the parameter yaml layout and citation layout

    """
    plugin_folder = savu_base_path + file_path
    title = module.split(".")
    capital_title = convert_title(title[-1]).replace(" ", "")
    file_str = plugin_folder + "_tools.py"
    generator_dir = savu_base_path + "scripts/plugin_generator/"
    param_definition_template = (
        generator_dir + "template_elements/parameter_definition.py"
    )

    if os.path.isfile(file_str):
        print("\nA tools file exists at " + file_str)
    else:
        with open(file_str, "w+") as new_tools_file:
            new_tools_file.write(get_tools_info(capital_title))
            append_file(new_tools_file, param_definition_template)

        print("A tools file has been created at:\n", file_str)


def get_tools_info(title):
    tools_info =\
'''from savu.plugins.plugin_tools import PluginTools

class ''' + title + '''Tools(PluginTools):
    """(Change this) A short description of the plugin"""
    
'''
    return tools_info


def create_documentation_template(
    file_path, module, savu_base_path, plugin_guide_path):
    # Locate documentation file
    plugin_path = file_path.replace("savu/", "")
    doc_folder = (
        savu_base_path + "doc/source/" + plugin_guide_path + plugin_path
    )
    title = module.split(".")
    file_str = doc_folder + "_doc.rst"
    doc_image_folder = (
        savu_base_path
        + "doc/source/files_and_images/"
        + plugin_guide_path
        + plugin_path
        + ".png"
    )

    if os.path.isfile(file_str):
        print("\nA documentation file exists at " + file_str)
    else:
        # Create the file directory for the documentation if it doesn't exist
        pu.create_dir(file_str)
        # Create the file for the documentation images
        pu.create_dir(doc_image_folder)
        doc_image_folder_inline = doc_image_folder.split("files_and_images/")[
            1
        ]
        with open(file_str, "w+") as new_rst_file:
            new_rst_file.write(":orphan:\n\n")
            new_rst_file.write(
                convert_title(title[-1])
                + " Documentation"
                + "\n##########################################"
                "#######################\n"
            )
            new_rst_file.write(
                "\n(Change this) Include your plugin "
                "documentation here. Use a restructured "
                "text format.\n"
            )
            new_rst_file.write("\n..")
            new_rst_file.write(
                "\n    This is a comment. Include an image "
                'or file by using the following text \n    "'
                ".. figure:: ../files_and_images/"
                + doc_image_folder_inline
                + '"\n'
            )
        print("A documentation file has been created at:\n", file_str)


def get_module_info(title):
    module_info =\
    '''
"""
.. module:: ''' + title + \
'''
   :platform: Unix
   :synopsis: (Change this) A template to create a simple plugin that takes 
    one dataset as input and returns a similar dataset as output.

.. moduleauthor:: (Change this) Developer Name <email@address.ac.uk>
"""
    '''
    return module_info


def convert_title(original_title):
    # Capwords is used so that the first letter following a number is
    # not capitalised. This would affect plugin names including '3d'
    original_title = original_title.split("/")[-1]
    return string.capwords(original_title.replace("_", " "))


def valid_name(plugin_name):
    """Return false if the plugin name is not valid.
    Plugin names must begin with a lowercase letter.
    """
    letters = [l for l in plugin_name]
    if isinstance(letters[0], str) and letters[0].islower():
        return True
    return False


def remove_plugin_files(file_path, savu_base_path, plugin_guide_path):
    """Delete plugin file, tools file and documentation file"""
    plugin_folder = savu_base_path + file_path
    file_str = plugin_folder + ".py"
    plugin_error_str = "No plugin file exists for this plugin."
    remove_file(file_str, plugin_error_str)

    # Delete tools file
    file_str = plugin_folder + "_tools.py"
    tools_error_str = "No tools file was located for this plugin."
    remove_file(file_str, tools_error_str)

    # Delete documentation file
    doc_file_path = file_path.replace("savu/", "")
    doc_folder = (
        f"{savu_base_path}doc/source/{plugin_guide_path}{doc_file_path}"
    )
    doc_file_str = doc_folder + "_doc.rst"
    doc_error_str = "No documentation file was located for this plugin."
    remove_file(doc_file_str, doc_error_str)


def check_decision(check):
    if check.lower() == "y":
        return True
    else:
        return False


def remove_file(file_str, error_str):
    """Remove the file at the provided file path

    :param file_str: The file path to the file to remove
    :param error_str: The error message to display
    """
    if os.path.isfile(file_str):
        os.remove(file_str)
        print("The file at:\n", file_str, "was removed.")
    else:
        print(error_str)


def check_plugin_exists(plugin_name):
    """Check if a plugin class is already registered inside Savu

    :param plugin_name:
    :return: True if found, module name for plugin
    """
    if not valid_name(plugin_name):
        raise ValueError(
            "Please write the plugin name in the format plugin_name with "
            "a lowercase letter as the first character and underscores in "
            "the place of spaces. For example, to create a plugin named "
            "Median Filter, type median_filter."
        )
    print("\nChecking if this plugin already exists..")
    plugin_title = convert_title(plugin_name).replace(" ", "")
    plugin = get_plugin_class(plugin_title)
    if plugin is None:
        plugin_module_name = plugin_name.replace("/", ".")
        module = "savu.plugins." + plugin_module_name
        return False, module
    print("This plugin does exist inside Savu.\n")
    return True, plugin.__module__


def main():
    args = __option_parser(doc=False)

    print("\n*******************************************************")
    print(" Please only use this command when you are working on")
    print(" your own Savu directory. New plugin files cannot be ")
    print(" saved to or deleted from the Diamond Light Source Savu ")
    print(" directory")
    print("*******************************************************")

    plugin_exists, module = check_plugin_exists(args.plugin_name)

    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split("scripts")[0]
    file_path = module.replace(".", "/")
    plugin_guide_path = "plugin_guides/"
    if args.delete is True:
        question_str = "Are you sure you want to delete all files for " \
                       "this plugin? [y/n]"
        if check_decision(check=input(question_str)) is True:
            remove_plugin_files(file_path, savu_base_path, plugin_guide_path)
        else:
            print("Plugin files were not removed.")
    else:
        print("*******************************************************")
        print(" Three files will be created: ")
        print(" * A plugin file \n * A plugin tools file \n"
              " * A file where you can describe how to use your "
              "plugin")
        print("*******************************************************")
        question_str_1 = f"Do you want the files to be saved inside " \
                       f"{savu_base_path}?"
        question_str = f"Do you want to view the paths to the current " \
                       f"plugin files?" if plugin_exists \
                       else question_str_1
        if check_decision(check=input(question_str)) is True:
            create_plugin_template(
                file_path, module, args.quick, savu_base_path)
            create_tools_template(file_path, module, savu_base_path)
            create_documentation_template(
                file_path, module, savu_base_path, plugin_guide_path)
            print(f"\nIf you want to delete all three files, use "
                  f"\n      savu_plugin_generator -d {args.plugin_name}\n")
        else:
            print("Exiting plugin generator.")


if __name__ == "__main__":
    main()
