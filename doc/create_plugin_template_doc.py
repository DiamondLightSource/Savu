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
.. module:: create_plugin_template_doc
   :platform: Unix
   :synopsis: A module to create plugin template rst files for documentation

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""

import os
import re

from collections import OrderedDict

import savu.plugins.utils as pu
import doc.create_plugin_doc as pdoc


def create_plugin_template_downloads(savu_base_path):
    """Inside plugin_examples/plugin_templates/general
    If the file begins with 'plugin_template' then select it
    Read the lines of the files docstring and set as a descriptor
    """
    dev_file_path = f"{savu_base_path}doc/source/dev_guides/"
    doc_template_file = f"{dev_file_path}dev_plugin_templates.rst"

    # Populate dictionary with template class and template class docstring
    docstring_text = create_template_class_dict(savu_base_path)
    if docstring_text:
        with open(doc_template_file, "w") as doc_template:
            doc_template.write(".. _plugin_templates:\n")
            doc_template.write("\n")
            doc_template.write(f"Plugin templates {pdoc.set_underline(6 ,23)}")
            doc_template.write("\n")

            doc_name = "plugin_template1_with_detailed_notes"
            detailed_template = docstring_text.get(doc_name)

            if detailed_template:
                docstring_text.pop(doc_name)
                title = pdoc.convert_title(doc_name)
                title, number = filter_template_numbers(title)
                # Create the restructured text page for the plugin template
                # python code
                generate_template_files(doc_name, title)
                inner_file_str = \
                    "../../../plugin_examples/plugin_templates/general"
                doc_template.write(f"{title}{pdoc.set_underline(3 ,66)}")
                doc_template.write(
                    "\nA template to create a simple plugin "
                    "that takes one dataset as input and returns "
                    "a similar dataset as output"
                )
                doc_template.write("\n")
                doc_template.write(
                    """
.. list-table::  
   :widths: 10

   * - :ref:`"""
                    + doc_name
                    + """`

"""
                )
            doc_template.write(f"Further Examples{pdoc.set_underline(3 ,66)}")
            # Begin the table layout
            doc_template.write(
                """
.. list-table::  
   :widths: 10 90
   :header-rows: 1

   * - Link
     - Description"""
            )

            for doc_name, doc_str in docstring_text.items():
                title = pdoc.convert_title(doc_name)
                title, number = filter_template_numbers(title)
                desc_str = doc_str["desc"]
                # Create a link to the restructured text page view of
                # the python code for the template
                doc_template.write("\n   * - :ref:`" + doc_name + "`")
                # The template description from the docstring
                doc_template.write("\n     - " + desc_str)
                doc_template.write("\n")
                # Create the restructured text page for the plugin template
                # python code
                generate_template_files(doc_name, title)

            doc_template.write("\n")


def generate_template_files(doc_name, title):
    """Create a restructured text file which will include the python
     code for the plugin template 'doc_name'

    :param doc_name: The name of the template file
    :param title:
    :return:
    """
    inner_file_str = "../../../../plugin_examples/plugin_templates/general"
    template_file_path = \
        f"{savu_base_path}doc/source/dev_guides/templates/{doc_name}.rst"

    with open(template_file_path, "w") as tfile:
        # Add the orphan instruction as this file is not inside a toctree
        tfile.write(":orphan:\n")
        tfile.write("\n.. _" + doc_name + ":\n")
        tfile.write("\n")
        tfile.write(f"{title}{pdoc.set_underline(4, 39)}")
        tfile.write("\n")
        tfile.write(_get_download_string(title, inner_file_str, doc_name))
        tfile.write("\n")
        tfile.write(_get_download_string(f"{title} Tools",
                                         inner_file_str,
                                         f"{doc_name}_tools"))
        tfile.write("\n")
        tfile.write(_get_include_string(doc_name))
        tfile.write("\n    :language: python\n")
        tfile.write("\n")
        tfile.write(_get_include_string(f"{doc_name}_tools"))
        tfile.write("\n    :language: python\n")


def _get_download_string(label, inner_file, doc_name):
    return f":download:`Download {label}<{inner_file}/{doc_name}.py>`\n\n"


def _get_include_string(doc_name):
    include_str = f".. literalinclude:: " \
                  f"/../../plugin_examples/plugin_templates/general/{doc_name}.py"
    return include_str


def filter_template_numbers(name_string):
    """
    :param name_string: The name of the template
    :return: A string with the template number seperated by a space
    """
    number = "".join(l for l in name_string if l.isdigit())
    letters = "".join(l for l in name_string if l.isalpha())
    split_uppercase = [l for l in re.split("([A-Z][^A-Z]*)", letters) if l]
    title = " ".join(split_uppercase)
    name = title + " " + number
    return name, number


def create_template_class_dict(savu_base_path):
    """Iterate through the plugin example folder and store the class
    and it's class docstring into a dictionary docstring_text

    :param savu_base_path:
    :return: docstring_text dictionary of class and docstring
    """
    docstring_text = {}
    plugin_ex_path = \
        f"{savu_base_path}plugin_examples/plugin_templates/general"

    for t_root, t_dirs, template_files \
            in os.walk(plugin_ex_path, topdown=True):
        template_files[:] = [fi for fi in template_files
                             if fi.split(".")[-1] == "py"
                             and "tools" not in fi]
        if "__" not in t_root:
            pkg_path = t_root.split("Savu/")[1]
            module_name = pkg_path.replace("/", ".")

        for fi in template_files:
            file_name = fi.split(".py")[0]
            cls_module = module_name + "." + file_name
            try:
                cls_loaded = pu.load_class(cls_module)()
            except AttributeError as e:
                cls_loaded = None

            if cls_loaded:
                tools = cls_loaded.get_plugin_tools()
                doc = tools.get_doc() if tools else ""
                desc = doc.get("verbose") if isinstance(doc ,dict) else ""
                title = pdoc.convert_title(file_name)
                name, number = filter_template_numbers(title)
                docstring_text[file_name] = {
                    "desc": desc,
                    "number": int(number),
                }

    # Order templates by number
    docstring_text = OrderedDict(
        sorted(docstring_text.items(), key=lambda i: i[1]["number"])
    )

    return docstring_text


if __name__ == "__main__":
    # determine Savu base path
    main_dir = \
        os.path.dirname(os.path.realpath(__file__)).split("/Savu/")[0]
    savu_base_path = f"{main_dir}/Savu/"

    # Create template download page
    create_plugin_template_downloads(savu_base_path)
