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
.. module:: savu_plugin_generator_test
   :platform: Unix
   :synopsis: A command line tool for creating Savu plugins

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""

import os
import unittest

import savu.plugins.utils as pu
import savu.test.test_process_list_utils as tplu
import savu.test.travis.framework_tests.plugin_coverage_test as pct


class SavuPluginGeneratorTest(unittest.TestCase):
    """
    For the test:  It should just be one test that runs through all the
    plugins and checks that four components exist:
            processing plugin
            plugin tools file
            plugin documentation
            plugin test
    If all four components do not exist then the test should break and
    output what is missing (for all plugins). It might be useful to output
    the paths to all "incomplete" plugin sets so we can easily clean up any
    suspicious files before a release.

    """

    def test_plugin_generator(self):
        self.check_directories()
        #TODO check registered plugins instead of directories

    def check_directories(self):
        """
        Get the current plugins and check which of these .py files also has
        a tools, documentation and test file. If there are specific files
        missing a .py file then highlight missing the plugin names.
        """
        savu_base_path = \
            os.path.dirname(os.path.realpath(__file__)).split('scripts')[0]

        plugin_coverage = pct.PluginCoverageTest()
        plugin_folder = plugin_coverage.get_plugin_list(savu_base_path
                                                      + 'savu/plugins')
        # Use the file and directory path
        plugin_files = tplu.get_all_files_from(savu_base_path
                                               + 'savu/plugins')

        self.check_plugin_tools(savu_base_path, plugin_files)
        self.check_plugin_documentation(savu_base_path, plugin_files)
        #self.check_plugin_tests(savu_base_path, plugin_folder,
        #                                         plugin_coverage)


    def check_plugin_tools(self, savu_base_path, plugin_files):
        """Check if there is a plugin tools file for each of the
        plugin files
        """
        plugin_tools_list = [p.split('_tools.py')[0]
                             for p in plugin_files
                                 if 'tools' in p]
        plugin_list = [p.split('.py')[0]
                       for p in plugin_files
                           if 'tools' not in p]

        plugins_with_tools = list(set(plugin_list)
                                  .intersection(set(plugin_tools_list)))
        plugins_without_tools = list(set(plugin_list)
                                     .difference(set(plugin_tools_list)))

        message = '\nThere are no tools files for the following plugins:'
        print(message, *plugins_without_tools, sep='\n- ')

    def check_plugin_documentation(self, savu_base_path, plugin_files):
        """Check if there is a plugin documentation file for each of the
        plugin files
        """
        # Get the relevant files with their directories
        plugin_doc_files = tplu.get_all_files_from(savu_base_path
                                    + 'doc/source/plugin_guides/plugins')

        plugin_list = [p.split('.py')[0]
                       for p in plugin_files
                           if 'tools' not in p]
        plugin_doc_list = [p.split('_doc.rst')[0]
                           for p in plugin_doc_files]

        plugins_with_doc = list(set(plugin_list)
                                .intersection(set(plugin_doc_list)))
        plugins_without_doc = list(set(plugin_list)
                                   .difference(set(plugin_doc_list)))

        message = '\nThere are no documentation files for the following ' \
                  'plugins:'
        print(message, *plugins_without_doc, sep='\n- ')


    def create_plugin_directories(self, savu_base_path, plugin_files):
        """ Create plugin directories inside documentation and
        documentation file and image folders
        """
        # Create directories inside
        doc_path = savu_base_path + 'doc/source/plugin_guides/plugins/'
        doc_image_path = savu_base_path \
            + 'doc/source/files_and_images/plugin_guides/plugins/'

        # find the directories to create
        for file in plugin_files:
            doc_dir = doc_path + file
            image_dir = doc_image_path + file
            pu.create_dir(doc_dir)
            pu.create_dir(image_dir)


if __name__ == "__main__":
    unittest.main()
