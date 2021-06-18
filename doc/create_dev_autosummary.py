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
.. module:: create_dev_autosummary
   :platform: Unix
   :synopsis: A module to automatically update a Sphinx developer API.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os


def add_folder(f):
    f.write('\n.. toctree::')
    f.write('\n   :glob:\n')
    f.write('\n   ../api_plugin/*\n')


def add_package_entry(f, root, dirs, files, output):
    pkg_path = root.split('Savu/')[1]
    module_name = pkg_path.replace('/', '.')
    f.write(module_name +
            '\n------------------------------------------------------------\n')

    f.write('\n.. toctree::\n')


def amend_folder(api_folder):
    all_files = []
    for (dirpath, dirnames, filenames) in os.walk(api_folder):
        all_files.extend(filenames)
        break

    for f in all_files:
        if f.split('test')[0] == 'savu.':
            os.remove(api_folder + '/' + f)
        else:
            s1 = f.split('plugins.')
            if len(s1) > 1:
                if s1[1] not in ['plugin.rst', 'plugin_datasets.rst']:
                    os.remove(api_folder + '/' + f)
    all_files = []
    for (dirpath, dirnames, filenames) in os.walk(api_folder):
        all_files.extend(filenames)
        break

    try:
        os.remove(api_folder + '/savu.rst')
        os.remove(api_folder + '/setup.rst')
        os.remove(api_folder + '/modules.rst')
        os.remove(api_folder + '/savu.core.rst')
        os.remove(api_folder + '/savu.data.rst')
        os.remove(api_folder + '/savu.data.data_structures.rst')
    except:
        pass

if __name__ == "__main__":

    # determine Savu base path
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('doc')[0]
    api_folder = savu_base_path + 'doc/source/reference/api_plugin'

    # open the autosummary file
    f = open(savu_base_path + 'doc/source/reference/dev_autosummary.rst', 'w')

    # add header
    f.write('API Documentation \n===================\n')
    f.write('Information on specific functions, classes, and methods.\n \n')

    amend_folder(api_folder)

    add_folder(f)
