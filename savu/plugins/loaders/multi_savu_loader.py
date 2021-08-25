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
.. module:: multi_savu_loader
   :platform: Unix
   :synopsis: A class for loading multiple savu output nexus files.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import os
import tempfile
import copy

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
from savu.plugins.loaders.savu_nexus_loader import SavuNexusLoader
from savu.data.data_structures.data_types.stitch_data import StitchData


@register_plugin
class MultiSavuLoader(BaseLoader):
    def __init__(self, name='MultiSavuLoader'):
        super(MultiSavuLoader, self).__init__(name)

    def setup(self):
        savu = self._get_savu_loader()
        data_obj_list = self._get_data_objects(savu)
        data_obj = self.exp.create_data_object('in_data', 'savu')

        # dummy file
        filename = os.path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        stack_or_cat = self.parameters['stack_or_cat']
        dim = self.parameters['stack_or_cat_dim']
        data_obj.data = StitchData(data_obj_list, stack_or_cat, dim)

        self._set_axis_labels(data_obj, data_obj_list[0])
        self._set_patterns(data_obj, data_obj_list[0])

        data_obj.set_original_shape(data_obj.data.get_shape())
        return data_obj

    def _set_axis_labels(self, data_obj, savu_obj):
        axis_labels = savu_obj.get_axis_labels()
        if self.parameters['stack_or_cat'] == 'stack':
            name, unit = self.parameters['axis_label'].split('.')
            axis_labels.append({name: unit})
        data_obj.data_info.set('axis_labels', axis_labels)

    def _set_patterns(self, data_obj, savu_obj):
        patterns = savu_obj.data_info.get('data_patterns')

        if self.parameters['stack_or_cat'] == 'stack':
            for p in patterns:
                patterns[p]['slice_dims'] += (3,)
        data_obj.data_info.set('data_patterns', patterns)

    def _get_data_objects(self, savu):
        rrange = self.parameters['range']
        file_list = list(range(rrange[0], rrange[1]+1))
        file_path = copy.copy(self.exp.meta_data.get('data_file'))
        file_name = '' if self.parameters['file_name'] is None else\
            self.parameters['file_name']

        data_obj_list = []
        for i in file_list:
            this_file = file_path + file_name + str(i) + '.h5'
            self.exp.meta_data.set('data_file', this_file)
            savu.setup()
            data_obj_list.append(self.exp.index['in_data']['tomo'])
            self.exp.index['in_data'] = {}

        self.exp.meta_data.set('data_file', file_path)
        return data_obj_list

    def _get_savu_loader(self):
        savu = SavuNexusLoader()
        savu.exp = self.exp
        savu._populate_default_parameters()
        savu.parameters['data_path'] = self.parameters['data_path']
        savu.parameters['name'] = self.parameters['name']
        return savu
