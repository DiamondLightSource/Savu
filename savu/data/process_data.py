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
.. module:: process_data
   :platform: Unix
   :synopsis: Class which describes the NeXus process description

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import h5py
import json
import os

import numpy as np


NX_CLASS = 'NX_class'


class ProcessList(object):
    """
    Descriptor for process lists loaded from file
    """

    def __init__(self):
        super(ProcessList, self).__init__()
        self.process_list = []
        self.name = "Default"

    def populate_process_list(self, filename):
        process_file = h5py.File(filename, 'r')
        self.name = os.path.basename(filename)
        process_group = process_file['entry/process']
        for key in process_group.keys():
            process = {}
            process['name'] = process_group[key]['name'][0]
            process['id'] = process_group[key]['id'][0]
            process['data'] = json.loads(process_group[key]['data'][0])
            self.process_list.append(process)
        process_file.close()

    def save_list_to_file(self, filename):
        process_file = h5py.File(filename, 'w')
        entry_group = process_file.create_group('entry')
        entry_group.attrs[NX_CLASS] = 'NXentry'
        processes_group = entry_group.create_group('process')
        processes_group.attrs[NX_CLASS] = 'NXprocess'
        count = 0
        for process in self.process_list:
            process_group = processes_group.create_group("%i" % count)
            process_group.attrs[NX_CLASS] = 'NXnote'
            id_array = np.array([process['id']])
            process_group.create_dataset('id', id_array.shape, id_array.dtype,
                                         id_array)
            name_array = np.array([process['name']])
            process_group.create_dataset('name', name_array.shape,
                                         name_array.dtype, name_array)
            data_array = np.array([json.dumps(process['data'])])
            process_group.create_dataset('data', data_array.shape,
                                         data_array.dtype, data_array)
            count += 1
        process_file.close()
