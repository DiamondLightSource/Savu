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
.. module:: plugin_coverage_test
   :platform: Unix
   :synopsis: Test that all the plugins are
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import unittest
import os
import fnmatch

from savu.data.plugin_list import PluginList
import savu.test.test_process_list_utils as tplu


class PluginCoverageTest(unittest.TestCase):

    def test_coverage(self):
        savu_base_path = \
            os.path.dirname(os.path.abspath(__file__)).split('savu/test/travis/framework_tests')[0]

        # lists all .nxs process lists used in the tests, and all plugins
        # directly called in the tests
        tests_plugins_dir = savu_base_path + 'savu/test'
        [nxs_in_tests, plugins_in_tests] = \
            tplu.get_process_list(tests_plugins_dir)

        # remove data files from the list
        data_list = self.get_data_list(savu_base_path + 'test_data/data')
        nxs_in_tests = list(set(nxs_in_tests).difference(set(data_list)))

        # since now some nxs files are in the subfolders, we need to make sure
        # that we extract the basename only (without the "head")
        nxs_in_tests_mod = []
        for nxs in nxs_in_tests:
            try:
                filename_nxs = os.path.basename(nxs)
                nxs_in_tests_mod.append(filename_nxs)
            except Exception:
                print("The failed basename file:", nxs)

        # list all test process lists available in test_process_lists folder
        test_process_path = savu_base_path + 'test_data/test_process_lists'
        self.nxs_avail = tplu.get_test_process_list(test_process_path)

        dir_plugin_path = savu_base_path + 'savu/plugins'
        # list the .nxs found in tests that are located in the
        # test_process_lists folder
        self.nxs_used = \
            list(set(nxs_in_tests).intersection(set(self.nxs_avail)))

        # which test process lists were not in the test_process_lists folder
        nxs_unused = list(set(nxs_in_tests).difference(set(self.nxs_avail)))
        print("===============================================================")
        print("\nThese .nxs test files were found inside the tests, but are "
              "not available in the test_process_lists folder:\n")
        for nxs in nxs_unused:
            associated_plugin = tplu.find_plugin_for_process_list(tests_plugins_dir, str(nxs))
            print("-->", nxs, "|||", os.path.relpath(str(associated_plugin), savu_base_path))
        print ("===============================================================")

        # get all plugins listed in self.nxs_used process lists
        tested_plugin_list = \
            self.get_test_plugin_list(self.nxs_used, test_process_path)
        tested_plugin_list += plugins_in_tests

        # list all plugins
        plugin_list = self.get_plugin_list(dir_plugin_path)

        print ("===============================================================")
        print ("\nThe following plugins are not covered by the tests:\n")
        uncovered = list(set(plugin_list).difference(set(tested_plugin_list)))
        for plugin in uncovered:
            for root, dirs, files in os.walk(dir_plugin_path):
                for name in files:
                    fname_type = os.path.splitext(name)[1]
                    if (fname_type == '.py'):
                        if fnmatch.fnmatch(name, plugin):
                            print("-->", name, "|||", os.path.relpath(root, savu_base_path))
        print ("===============================================================")
        print ("===============================================================")
        print("\nThe following process lists are redundant:\n")
        redundant = list(set(self.nxs_avail).difference(set(self.nxs_used)))
        for plugin in redundant:
            for root, dirs, files in os.walk(test_process_path):
                for name in files:
                    if fnmatch.fnmatch(name, plugin):
                        print("-->", name, "|||", os.path.relpath(root, savu_base_path))
        print("===============================================================")

    def test_process_lists(self):
        # check for unused process lists
        pass

    def get_data_list(self, folder):
        data_list = []
        ftypes = ['nxs', 'h5']
        exclude_dir = ['__pycache__']
        exclude_file = ['__init__.py']
        for root, dirs, files in os.walk(folder, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude_dir]
            files[:] = [fi for fi in files if fi.split('.')[-1] in ftypes]
            files[:] = [fi for fi in files if fi not in exclude_file]
            for f in files:
                data_list.append(f)
        return data_list

    def get_test_plugin_list(self, process_files, path):
        plugin_names = []
        for pfile in process_files:
            plist = PluginList()
            try:
                plist._populate_plugin_list(path + '/' + pfile)
                plugin_names = self.get_plugin_names(plist, plugin_names)
            except OSError as e:
                print(f"ERROR with {pfile}: {e}")
        return list(set(plugin_names))

    def get_plugin_names(self, plist, plugin_names):
        for p in plist.plugin_list:
            try:
                plugin_id = p['id']
                pList = self.add_plugin(plugin_id)
                for p in pList:
                    plugin_names.append(p + '.py')
            except ImportError as e:
                print("Failed to run test as libraries not available (%s),"
                      % (e) + " passing test")
        return plugin_names

    def add_plugin(self, plugin_id):
        plugin_list = []
        plugin = self.load_plugin(plugin_id)
        pList = plugin.__class__.mro()
        for p in pList:
            module_name = p.__module__.split('.')
            if module_name[0] == 'savu':
                plugin_list.append(module_name[-1])
        return plugin_list

    def get_plugin_list(self, folder):
        plugin_list = []
        exclude_dir = ['__pycache__']
        exclude_file = ['__init__.py']
        for root, dirs, files in os.walk(folder, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude_dir]
            files[:] = [fi for fi in files if fi not in exclude_file]
            files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
            for f in files:
                plugin_list.append(f)
        return plugin_list

    def load_plugin(self, name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        module_name = name.split('.')[-1]
        mod2class = ''.join(x.capitalize() for x in module_name.split('_'))
        clazz = getattr(mod, mod2class.split('.')[-1])()
        return clazz

    # Addition to allow access to this class from another test class
    def runTest(self):
        pass

if __name__ == "__main__":
    unittest.main()
