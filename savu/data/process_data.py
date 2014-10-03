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
import logging

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

    def add_process_citation(self, filename, process_number, citation):
        logging.debug("Adding Citation to file %s", filename)
        process_file = h5py.File(filename, 'a')
        process_entry = process_file['entry/process/%i' % process_number]
        citation.write(process_entry)
        process_file.close()

    def add_intermediate_data_link(self, filename, output_data, group_name):
        logging.debug("Adding link to file %s", filename)
        process_file = h5py.File(filename, 'a')
        inter_entry = process_file['entry'].require_group('intermediate')
        inter_entry.attrs[NX_CLASS] = 'NXcollection'
        inter_entry[group_name] = output_data.external_link()
        process_file.close()


class CitationInfomration(object):
    """
    Descriptor of Citation Information for processes
    """

    def __init__(self):
        super(CitationInfomration, self).__init__()
        self.description = "Default Description"
        self.doi = "Default DOI"
        self.endnote = "Default Endnote"
        self.bibtex = "Default Bibtex"

    def write(self, hdf_group):
        citation_group = hdf_group.create_group('citation')
        citation_group.attrs[NX_CLASS] = 'NXcite'
        description_array = np.array([self.description])
        citation_group.create_dataset('description',
                                      description_array.shape,
                                      description_array.dtype,
                                      description_array)
        doi_array = np.array([self.doi])
        citation_group.create_dataset('doi',
                                      doi_array.shape,
                                      doi_array.dtype,
                                      doi_array)
        endnote_array = np.array([self.endnote])
        citation_group.create_dataset('endnote',
                                      endnote_array.shape,
                                      endnote_array.dtype,
                                      endnote_array)
        bibtex_array = np.array([self.bibtex])
        citation_group.create_dataset('bibtex',
                                      bibtex_array.shape,
                                      bibtex_array.dtype,
                                      bibtex_array)
