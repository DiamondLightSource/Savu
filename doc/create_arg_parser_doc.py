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
.. module:: create_arg_parser_doc
   :platform: Unix
   :synopsis: A module to create savu arg parser documentation

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""

import os

import doc.create_plugin_doc as pdoc
import scripts.config_generator.savu_config as sc


def create_savu_config_documentation(savu_base_path):
    """Look at the available commands inside savu_config
    Create a rst text file for each.
    """
    reference_file_path = f"{savu_base_path}doc/source/reference/"
    command_file_path = f"{reference_file_path}savu_config_commands.rst"

    with open(command_file_path, "w") as cfile:
        savu_command_test_start = """
Savu Config Commands
**********************

The links on this page provide help for each command.
If you are using the command line please type ``-h`` or ``--help``.

.. code-block:: bash

   savu_config --help

"""
        # Write contents
        cfile.write(savu_command_test_start)
        for command in sc.commands:
            cfile.write("\n")
            cfile.write("* :ref:`" + command + "`")
            cfile.write("\n")

        # Document commands
        for command in sc.commands:
            cfile.write("\n")
            cfile.write(".. _" + command + ":")
            cfile.write("\n\n" + command)
            cfile.write(pdoc.set_underline(3, 16))
            cfile.write("\n.. cssclass:: argstyle\n")
            cfile.write("\n    .. argparse::")
            cfile.write("\n            :module: scripts.config_generator.arg_parsers")
            cfile.write("\n            :func: _" + command + "_arg_parser")
            cfile.write("\n            :prog: " + command)
            cfile.write("\n")
            cfile.write("\n")


if __name__ == "__main__":
    # determine Savu base path
    main_dir = os.path.dirname(os.path.realpath(__file__)).split("/Savu/")[0]
    savu_base_path = f"{main_dir}/Savu/"

    # Create savu_config command rst files
    create_savu_config_documentation(savu_base_path)
