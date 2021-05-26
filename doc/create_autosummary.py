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
.. module:: create_autosummary
   :platform: Unix
   :synopsis: A module to automatically update a Sphinx API.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os


def list_of_packages(base_path):
    pkg_list = []
    for entry in os.listdir(base_path):
        entry_path = os.path.join(base_path, entry)
        if not os.path.isfile(entry_path):
            pkg_list.append(entry_path)
    return pkg_list


def add_package_entry(f, root, dirs, files, output):
    pkg_path = root.split('Savu/')[1]
    module_name = pkg_path.replace('/', '.')
    f.write(module_name +
            '\n------------------------------------------------------------\n')
    f.write('\n.. toctree::\n')

    for fi in files:
        file_path = module_name + '.' + fi.split('.py')[0]
        f.write('   ' + output + '/' + file_path + '\n')
    f.write('\n\n')


def add_indices_and_tables(f):
    f.write('Indices and tables\n')
    f.write('==================\n')
    f.write('* :ref:`genindex`\n')
    f.write('* :ref:`modindex`\n')
    f.write('* :ref:`search`\n')


if __name__ == "__main__":
    import sys
    out_folder, rst_file, api_type = sys.argv[1:]

    # determine Savu base path
    savu_base_path = \
        os.path.dirname(os.path.realpath(__file__)).split('doc')[0]

    # open the autosummary file
    f = open(savu_base_path + 'doc/source/reference/' + rst_file, 'w')

    if api_type == 'framework':
        f.write('Framework API \n===================\n')
        exclude_dir = ['__pycache__', 'test', 'plugins']
    elif api_type == 'plugin':
        f.write('Plugin API \n===================\n')
        exclude_dir = ['__pycache__', 'test']
    else:
        raise Exception('Unknown API type', api_type)

    # add header
    f.write('Information on specific functions, classes, and methods.\n \n')

    base_path = savu_base_path + 'savu'
    # create entries in the autosummary for each package

    exclude_file = ['__init__.py', 'win_readline.py']

    for root, dirs, files in os.walk(base_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dir]
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']
        files[:] = [fi for fi in files if fi not in exclude_file]
        if '__' not in root:
            add_package_entry(f, root, dirs, files, out_folder)

#    add_indices_and_tables(f)
