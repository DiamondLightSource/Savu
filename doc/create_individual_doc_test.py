# Copyright 2020 Diamond Light Source Ltd.
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
.. module:: create_individual_doc_test
   :platform: Unix
   :synopsis: A module to automatically create plugin documentation
.. moduleauthor:: Jessica Verschoyle

"""
import os

import savu.plugins.utils as pu

def create_plugin_doc_testing_file(savu_base_path, module_name, file_path):
    """ Open the provided file path. Read the lines beginning with a command
    prompt and save these to a list. Write these lines to a unittest file.

    :param savu_base_path:
    :param module_name: plugin module name
    :param file_path: plugin documentation file path
    """
    # Read the testing lines from the plugin documentation file
    doc_file_path = savu_base_path + module_name + '/' + file_path
    testing_lines, process_lists = read_test_file(doc_file_path)

    # If there are testing lines and/or process lists inside the plugin
    # documentation, then append the configurator end lines for use with
    # the unittest
    plugin_directory = module_name.split('plugins')[1]
    if testing_lines:
        file_name = file_path.split('.')[0]
        create_unittest(file_name, testing_lines, process_lists, plugin_directory)

def create_unittest(file_name , testing_lines, process_lists, plugin_directory):
    """ Create a unittest file

    :param file_name: Plugin file name
    :param testing_lines: Command lines to test
    :param process_lists: List of process list file paths to check
    :param log_directory: Plugin directory to save the log files inside
    """
    unittest_file_path = savu_base_path \
                         + 'savu/test/travis/doc_tests/plugins/' \
                         + plugin_directory +'/'+ file_name + '_test.py'
    pu.create_dir(unittest_file_path)

    unittest_setup = get_unittest_setup(file_name)
    setup_function = get_logging_set_up(plugin_directory, file_name)

    if testing_lines:
        unittest_config_start, unittest_config_end, test_list \
            = get_unittest_commands(testing_lines, process_lists, file_name)

    # If there are process lists inside the doc file, create a refresh function
    if process_lists:
        unittest_process_start, unittest_process_end, process_list_format = \
            get_unittest_process_list_function(process_lists)

    unittest_main = '''
    
    if __name__ == "__main__":
           unittest.main()
    '''

    with open(unittest_file_path, "w") as unittest_file:
        unittest_file.write(unittest_setup)
        unittest_file.write(setup_function)

        if process_lists:
            unittest_file.write(unittest_process_start)
            unittest_file.writelines(process_list_format)
            unittest_file.write(unittest_process_end)

        if testing_lines:
            unittest_file.write(unittest_config_start)
            unittest_file.writelines(test_list)
            unittest_file.write(unittest_config_end)

        unittest_file.write(unittest_main)
    unittest_file.close()

def get_logging_set_up(plugin_directory, file_name):
    """ Create the log handlers unittest function

    :param plugin_directory: The plugin file directory
    :param file_name: plugin file name
    :return: logging_handlers

    """
    folder_name = file_name.replace('_doc', '')
    logging_handlers = '''
    def setUp(self):
        """ Set up file handlers for the log and rst file.

        :param out_path: The file path to the directory to save to
        """
        doc_test_path = 'savu/test/travis/doc_tests/'
        plugin_log_file = doc_test_path +'logs''' \
                   + plugin_directory + '/' + folder_name + '''/'
        out_path = savu_base_path + plugin_log_file
        # Create directory if it doesn't exist
        pu.create_dir(out_path)

        logging.config.fileConfig(savu_base_path + doc_test_path \\
                                    + 'logging.conf')

        logger = logging.getLogger('documentationLog')
        dtu.add_doc_log_handler(logger, out_path)

        logger_rst = logging.getLogger('documentationRst')
        dtu.add_doc_rst_handler(logger_rst, out_path)

        print('The log files are inside the directory '+out_path)
        '''
    return logging_handlers

def get_unittest_process_list_function(process_lists):
    """ Create function to refresh process lists

    :param process_lists: List of process list file paths
    :return: refresh_process_start, refresh_process_end, process_list_format
    """
    # Set up the indentation for the proces list
    indent = 25 * ' '
    newline_str = ',\n'+indent
    # Create the list as a string
    process_list_format = map(lambda x: '\"' + x + '\"', process_lists)
    process_list_format =  (newline_str.join(map(str, process_list_format)))

    refresh_process_start = '''
    def refresh_process_lists(self):
        """ Run through the process list files and refresh them to update
        any inconsistent parameter values.
        If there is a value which cannot be used, that parameter will be set
        to the default value.
        """
        process_lists = ['''
    refresh_process_end = ''']
        output_checks = ['Exception','Error','ERROR']

        logger = logging.getLogger('documentationLog')

        for process_list_path in process_lists:
            file_exists = os.path.exists(savu_base_path + process_list_path)
            error_msg = 'The process list at ' + process_list_path + ' does not exist.'
            self.assertTrue(file_exists, msg=error_msg)
            if file_exists:
                # Write the process list being tested to the logger
                logger.debug('TEST PROCESS LIST: ' + savu_base_path + process_list_path)
                saved_stdout = sys.stdout
                try:
                    out = StringIO()
                    sys.stdout = out
                    tplu.refresh_process_file(savu_base_path + process_list_path)
                    output_value = out.getvalue().strip()
                    for check in output_checks:
                        error_msg = 'Refresh failed: ' + check + ' in the output.'
                        assert check not in output_value, error_msg
                finally:
                    sys.stdout = saved_stdout
        '''
    return refresh_process_start, refresh_process_end, process_list_format


def get_unittest_commands(testing_lines, process_lists, file_name):
    """ Set up the method for testing savu configurator commands

    :param testing_lines: The command lines to test
    :return: unittest_function_start, unittest_function_end, test_list
    """

    # Set up the indentation for the command list
    indent = 22 * ' '
    newline_str = '\",\n' + indent
    # Create the list as a string
    test_list = map(lambda x: '\"' + x + newline_str, testing_lines)

    # Set up the unittest
    unittest_function_start = '''    
    def test_''' + file_name + '''(self):
        """ Run the input commands with savu_config
        """
        '''
    if process_lists:
        unittest_function_start += 'self.refresh_process_lists()'

    unittest_function_start += '''
        input_list = ['''
    unittest_function_end = '''"exit", "y"]
        output_checks = ['Exception','Error','ERROR']
        sctu.savu_config_runner(input_list, output_checks, 
                                error_str=True)'''
    return unittest_function_start, unittest_function_end, test_list

def read_test_file(doc_file_path):
    """ Read the command prompt lines from the doc file and append to list

    :param doc_file_path:
    :return: testing_lines, process_lists
    """
    testing_lines = []
    process_lists = []
    with open(doc_file_path, 'r') as doc_file:
        for line in doc_file:
            if '>>>' in line:
                line = line.replace('>>>', '')
                testing_lines.append(line.strip())
            if '.. ::process_list::' in line:
                # Documentation must include this line in order to update
                # the plugin list before running it in the example
                # '.. ' indicates a rst file comment
                line = line.replace('.. ::process_list::', '')
                process_lists.append(line.strip())

    doc_file.close()
    return testing_lines, process_lists

def get_unittest_setup(file_name):
    """ Setup unittest

    :param file_name: Plugin name
    :return: unittest_setup
    """
    unittest_name = file_name.replace('_', ' ').title().replace(' ','')
    unittest_setup='''
"""
.. module:: ''' + file_name + '''_test
   :platform: Unix
   :synopsis: unittest test for plugin restructured text file documentation
.. moduleauthor: Jessica Verschoyle

"""
from __future__ import print_function

import os
import sys
import unittest
import logging
import logging.config

from StringIO import StringIO

import savu.plugins.utils as pu
import savu.test.test_process_list_utils as tplu
import savu.test.travis.doc_tests.doc_test_utils as dtu
import scripts.configurator_tests.savu_config_test_utils as sctu

# Determine Savu base path
savu_base_path = \\
os.path.dirname(os.path.realpath(__file__)).split('savu')[0]

class '''+unittest_name+'''Test(unittest.TestCase):
'''
    return unittest_setup


if __name__ == "__main__":
    # determine Savu base path
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('doc')[0]

    plugin_doc_file_path = savu_base_path + 'doc/source/documentation/plugins/'

    for root, dirs, files in os.walk(plugin_doc_file_path, topdown=True):
        if '__' not in root:
            pkg_path = root.split('Savu/')[1]
            module_name = pkg_path.replace('savu/', '')
            for file in files:
                file_name = file.split('.')[0]
                unittest_file_path = savu_base_path \
                                     + 'savu/test/travis/doc_tests/' \
                                     + file_name + '_test.py'

                # Read the testing lines from the plugin documentation file
                create_plugin_doc_testing_file(savu_base_path,
                                            module_name, file)
