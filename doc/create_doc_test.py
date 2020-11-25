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
.. module:: create_doc_test
   :platform: Unix
   :synopsis: A module to automatically create plugin documentation
.. moduleauthor:: Jessica Verschoyle

"""

import os

def create_plugin_doc_testing_files(savu_base_path, module_name, file_path):
    """ Open the provided file. Read the lines beginning with a command
    prompt and save these to a list. Write these lines to a unittest file.

    :param savu_base_path:
    :param module_name:
    :param file_path:
    """
    # Read the testing lines from the plugin documentation file
    doc_file_path = savu_base_path + module_name + '/' + file_path
    testing_lines = read_test_file(doc_file_path)

    file_name = file_path.split('.')[0]

    # If there are testing lines inside the plugin documentation then
    # append the configurator end lines for use with the unittest
    if testing_lines:
        indent = 22*' '
        newline_str = '\",\n'+indent
        # Create the list as a string
        test_list = map(lambda x: '\"'+ x + newline_str, testing_lines)

        # Set up the unittest
        unittest_function_start = '''    
    def test_'''+ file_name +'''(self):
        input_list = ['''
        unittest_function_end = '''"exit", "y"]
        output_checks = ['Exception']
        self.savu_config_runner(input_list, output_checks, 
                                error_str=True)
    '''
        unittest_file_path = savu_base_path \
                + 'savu/test/travis/framework_tests/plugin_rst_test.py'
        with open(unittest_file_path, "a") as unittest_file:
            unittest_file.write(unittest_function_start)
            unittest_file.writelines(test_list)
            unittest_file.write(unittest_function_end)
        unittest_file.close()


def read_test_file(doc_file_path):
    """ Read the command prompt lines from the doc file and append to list"""
    testing_lines = []
    with open(doc_file_path, 'r') as doc_file:
        for line in doc_file:
            if '>>>' in line:
                line = line.replace('>>>', '')
                testing_lines.append(line.strip())
    doc_file.close()
    return testing_lines


def create_plugin_rst_test_file():
    unittest_setup='''
"""
.. module:: plugin_rst_test
   :platform: Unix
   :synopsis: unittest test for plugin restructured text file documentation
.. moduleauthor: Jessica Verschoyle

"""

from __future__ import print_function

import sys
import unittest
from mock import patch
from StringIO import StringIO

from scripts.config_generator import savu_config


class PluginRstTest(unittest.TestCase):

    def savu_config_runner(self, input_list, output_checks,
                           error_str=False):
        """ Run savu_config with a list of input commands
        
        :param input_list: List of commands for the savu_config
        :param output_checks: List of strings which should be in the
          program output
        :param error_str: If true, then make sure that the error message 
         is not displayed inside the output text
        """
        with patch('__builtin__.raw_input', side_effect=input_list):
            saved_stdout = sys.stdout
            try:
                out = StringIO()
                sys.stdout = out
                savu_config.main()
                output = out.getvalue().strip()
                for check in output_checks:
                    if error_str:
                        assert check not in output
                    else:
                        assert check in output
            finally:
                sys.stdout = saved_stdout
'''

    unittest_file_path = savu_base_path \
                         + 'savu/test/travis/framework_tests/plugin_rst_test.py'
    with open(unittest_file_path, "w") as unittest_file:
        # Writing test to a file
        unittest_file.write(unittest_setup)
    unittest_file.close()


def close_plugin_rst_test_file():
    """ Include the ending call to main inside the test file
    """
    unittest_main='''

if __name__ == "__main__":
        unittest.main()

'''
    unittest_file_path = savu_base_path \
                         + 'savu/test/travis/framework_tests/plugin_rst_test.py'
    with open(unittest_file_path, "a") as unittest_file:
        unittest_file.write(unittest_main)
    unittest_file.close()


if __name__ == "__main__":
    # determine Savu base path
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('doc')[0]

    plugin_doc_file_path = savu_base_path + 'doc/source/documentation/plugins/'

    create_plugin_rst_test_file()

    for root, dirs, files in os.walk(plugin_doc_file_path, topdown=True):
        if '__' not in root:
            pkg_path = root.split('Savu/')[1]
            module_name = pkg_path.replace('savu/', '')
            for file in files:
                # Create tests from rst template lines with a prompt
                create_plugin_doc_testing_files(savu_base_path,
                                            module_name, file)
    close_plugin_rst_test_file()
