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
.. module:: hdf5_saver
   :platform: Unix
   :synopsis: A class to save data to a hdf5 output file.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import os
import copy

from savu.plugins.savers.utils.hdf5_utils import Hdf5Utils
from savu.plugins.savers.base_saver import BaseSaver
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.data.chunking import Chunking

@register_plugin
class Hdf5Saver(BaseSaver, CpuPlugin):
    def __init__(self, name='Hdf5Saver'):
        super(Hdf5Saver, self).__init__(name)
        self.in_data = None
        self.out_data = None
        self.data_name = None
        self.filename = None
        self.group_name = None

    def pre_process(self):
        # Create the hdf5 output file
        self.hdf5 = Hdf5Utils(self.exp)
        self.in_data = self.get_in_datasets()[0]
        self.data_name = self.in_data.get_name()
        current_pattern = self.__set_current_pattern()
        pattern_idx = {'current': current_pattern, 'next': []}

        self.filename = self.__get_file_name()
        self.group_name = self._get_group_name(self.data_name)
        logging.debug("creating the backing file %s", self.filename)
        self.backing_file = self.hdf5._open_backing_h5(self.filename, 'w')
        group = self.backing_file.create_group(self.group_name)
        group.attrs['NX_class'] = 'NXdata'
        group.attrs['signal'] = 'data'
        self.exp._barrier()
        shape = self.in_data.get_shape()
        chunking = Chunking(self.exp, pattern_idx)
        dtype = self.in_data.data.dtype
        chunks = chunking._calculate_chunking(shape, dtype)
        self.exp._barrier()
        self.out_data = self.hdf5.create_dataset_nofill(
                group, "data", shape, dtype, chunks=chunks)

    def process_frames(self, data):
        self.out_data[self.get_current_slice_list()[0]] = data[0]

    def post_process(self):
        self._link_datafile_to_nexus_file(self.data_name, self.filename,
                                          self.group_name + '/data')
        self.backing_file.close()

    def __set_current_pattern(self):
        pattern = copy.deepcopy(self.in_data._get_plugin_data().get_pattern())
        pattern[list(pattern.keys())[0]]['max_frames'] = self.get_max_frames()
        return pattern

    def get_pattern(self):
        if self.parameters['pattern'] != 'optimum':
            return self.parameters['pattern']
        previous_pattern = self.get_in_datasets()[0].get_previous_pattern()
        if previous_pattern:
            return list(previous_pattern.keys())[0]
        return list(self.get_in_datasets()[0].get_data_patterns().keys())[0]

    def __get_file_name(self):
        nPlugin = self.exp.meta_data.get('nPlugin')
        plugin_dict = \
            self.exp._get_experiment_collection()['plugin_dict'][nPlugin]
        fname = self.data_name + '_p' + str(nPlugin) + '_' + \
            plugin_dict['id'].split('.')[-1] + '.h5'
        out_path = self.exp.meta_data.get('out_path')
        return os.path.join(out_path, fname)
