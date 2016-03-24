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

from savu.data.plugin_list import PluginList


class PluginCoverageTest(unittest.TestCase):

    def test_coverage(self):
        savu_base_path = \
            os.path.dirname(os.path.realpath(__file__)).split('savu')[0]

        # lists all .nxs process lists used in the tests, and all plugins
        # directly called in the tests
        [nxs_in_tests, plugins_in_tests] = \
            self.get_process_list(savu_base_path + '/savu/test')

        # remove data files from the list
        data_list = self.get_data_list(savu_base_path + '/test_data/data')
        nxs_in_tests = list(set(nxs_in_tests).difference(set(data_list)))

        # list all test process lists available in test_process_lists folder
        test_process_path = savu_base_path + 'test_data/test_process_lists'
        self.nxs_avail = self.get_test_process_list(test_process_path)

        # list the .nxs found in tests that are located in the
        # test_process_lists folder
        self.nxs_used = \
            list(set(nxs_in_tests).intersection(set(self.nxs_avail)))

        # which test process lists were not in the test_process_lists folder
        nxs_unused = list(set(nxs_in_tests).difference(set(self.nxs_avail)))
        print "==============================================================="
        print ("\nThese .nxs test files were found inside the tests, but are "
               "not available in the test_process_lists folder:\n")
        for nxs in nxs_unused:
            print nxs
        print "==============================================================="

        # get all plugins listed in self.nxs_used process lists
        tested_plugin_list = \
            self.get_test_plugin_list(self.nxs_used, test_process_path)
        tested_plugin_list += plugins_in_tests

        # list all plugins
        plugin_list = self.get_plugin_list(savu_base_path + '/savu/plugins')

        print "==============================================================="
        print ("\nThe following plugins are not covered by the tests:\n")
        uncovered = list(set(plugin_list).difference(set(tested_plugin_list)))
        for plugin in uncovered:
            print plugin
        print "==============================================================="

        print "==============================================================="
        print ("\nThe following process lists are redundant:\n")
        redundant = list(set(self.nxs_avail).difference(set(self.nxs_used)))
        for plugin in redundant:
            print plugin
        print "==============================================================="

    def test_process_lists(self):
        # check for unused process lists
        pass

    def get_process_list(self, folder, search=False):
        process_list = []
        plugin_list = []
        exclude_dir = ['__pycache__']
        exclude_file = ['__init__.py']
        for root, dirs, files in os.walk(folder, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude_dir]
            files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
            files[:] = [fi for fi in files if fi not in exclude_file]
            processes = self.get_process_list_in_file(root, files)
            plugins = self.get_no_process_list_tests(root, files)
            for p in processes:
                process_list.append(p)
            for p in plugins:
                plugin_list.append(p)
        return process_list, plugin_list

    def get_process_list_in_file(self, root, files):
        processes = []
        for fname in files:
            fname = root + '/' + fname
            in_file = open(fname, 'r')
            for line in in_file:
                if '.nxs' in line:
                    processes.append(self.get_nxs_file_name(line))
        return processes

    def get_nxs_file_name(self, line):
        split_list = line.split("'")
        for entry in split_list:
            if 'nxs' in entry:
                if (len(entry.split(' ')) == 1):
                    return entry

    def get_no_process_list_tests(self, root, files):
        processes = []
        for fname in files:
            fname = root + '/' + fname
            in_file = open(fname, 'r')
            func = 'run_protected_plugin_runner_no_process_list'
            exclude = ['def', 'search_str']
            pos = 1
            param = self.get_param_name(func, pos, in_file, exclude=exclude)
            if param:
                in_file.seek(0)
                plugin_id_list = self.get_param_value_from_file(param, in_file)
                for pid in plugin_id_list:
                    plugin_name = pid.split('.')[-1].split("'")[0]
                    processes.append(plugin_name + '.py')
        return processes

    def get_param_name(self, func, pos, in_file, exclude=[]):
        """ Find the name of an argument passed to a function.

        :param str func: function name
        :param int pos: function argument position
        :param file in_file: open file to search
        :keyword list[str] exclude: ignore lines containing these strings.
                                    Defaults to [].
        :returns: name associated with function argument
        :rtype: str
        """
        search_str = 'run_protected_plugin_runner_no_process_list('
        ignore = ['def', 'search_str']
        val_str = None
        for line in in_file:
            if search_str in line:
                if not [i in line for i in ignore].count(True):
                    if ')' not in line:
                        line += next(in_file)
                    params = line.split('(')[1].split(')')[0]
                    val_str = params.split(',')[1].strip()
        return val_str

    def get_param_value_from_file(self, param, in_file):
        """ Find all values associated with a parameter name in a file.

        :param str param: parameter name to search for
        :param file in_file: open file to search
        :returns: value associated with param
        :rtype: list[str]
        """
        param_list = []
        for line in in_file:
            if param in line and line.split('=')[0].strip() == param:
                if "\\" in line:
                    line += next(in_file)
                    line = ''.join(line.split('\\'))
                value = line.split('=')[1].strip()
                param_list.append(value)
        return param_list

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

    def get_test_process_list(self, folder):
        test_process_list = []
        for root, dirs, files in os.walk(folder, topdown=True):
            files[:] = [fi for fi in files if fi.split('.')[-1] == 'nxs']
            for f in files:
                test_process_list.append(f)
        return test_process_list

    def get_test_plugin_list(self, process_files, path):
        plugin_names = []
        for pfile in process_files:
            print pfile
            plist = PluginList()
            plist._populate_plugin_list(path + '/' + pfile)
            for p in plist.plugin_list:
                plugin_id = p['id']
                pList = self.add_plugin(plugin_id)
                for p in pList:
                    plugin_names.append(p + '.py')
        return list(set(plugin_names))

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
            files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
            files[:] = [fi for fi in files if fi not in exclude_file]
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

if __name__ == "__main__":
    unittest.main()
