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
.. module:: savu_loader
   :platform: Unix
   :synopsis: A class for loading savu output data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import numpy as np

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin


@register_plugin
class SavuNexusLoader(BaseLoader):
    """
    A class to load all datasets, and associated metadata, from a Savu output
    nexus file.

    # remove preview parameter from here?!
    # option to choose which datasets to load and from which point?
    """

    def __init__(self, name='SavuNexusLoader'):
        super(SavuNexusLoader, self).__init__(name)

    def setup(self):
        print "\nsetup\n"

        datasets = []
        with h5py.File(self.exp.meta_data.get('data_file'), 'r') as nxsfile:
            datasets = self._read_nexus_file(nxsfile, datasets)
            datasets = self._last_unique_datasets(datasets)
            print datasets
            self._create_datasets(nxsfile, datasets)

    # what about if the data is a different type?  e.g. ImageKey, etc...
    # need to output the type of the data object?

    def _read_nexus_file(self, nxsfile, datasets):
        # only read the final instance of data relating to a particular dataset name
        # don't forget MPI mode!!!
        # find NXdata
        for key, value in nxsfile.items():
            if self._is_nxdata(value):
                datasets.append(self._get_dataset_info(key, value))
            elif isinstance(value, h5py.Group):
                self._read_nexus_file(value, datasets)
        return datasets

    def _is_nxdata(self, value):
        check = 'NX_class' in value.attrs.keys() and\
            value.attrs['NX_class'] == 'NXdata'
        return check

    def _get_dataset_info(self, key, value):
        import unicodedata
        key = unicodedata.normalize('NFKD', key).encode('ascii', 'ignore')
        ksplit = key.split('-')

        if len(ksplit) == 1 and ''.join(key.split('_')[0:2]) == 'finalresult':
            name = '_'.join(key.split('_')[2:])
            pos = 1000  # arbitrarily large number
        else:
            name = ''.join(ksplit[2:])
            pos = ksplit[0]
        return {'name': name, 'pos': pos, 'group': value}

    def _last_unique_datasets(self, datasets):
        all_names = list(set([d['name'] for d in datasets]))
        entries = {}
        for n in all_names:
            this_name = [d for d in datasets if d['name'] == n]
            max_pos = np.max(np.array([int(d['pos']) for d in this_name]))
            entries[n] = \
                [d['group'] for d in this_name if d['pos'] == max_pos][0]
        return entries

    def _create_datasets(self, nxsfile, datasets):
        inFile = nxsfile.filename
        data_objs = []
        for name, group in datasets.iteritems():
            dObj = self.exp.create_data_object('in_data', name)
            dObj.backing_file = h5py.File(inFile, 'r')
            self._read_nexus_group(group, dObj)
            dObj.set_shape(dObj.data.shape)
            self.set_data_reduction_params(dObj)
#            if isinstance(dObj.data, ImageKey):
#                dObj.data._set_dark_and_flat()
            data_objs.append(dObj)
        return data_objs

    def _read_nexus_group(self, group, dObj):
        dObj.data = group.get(group.attrs['signal'])
        self._add_axis_labels(dObj, group)
        self._add_patterns(dObj, group)
        self._add_meta_data(dObj, group)

    def _add_axis_labels(self, dObj, group):
        axes = group.attrs['axes']
        ordered_axes = [None]*len(axes)
        for i in range(len(axes)):
            ordered_axes[group.attrs['_'.join((axes[i], 'indices'))]] = axes[i]

        axis_labels = []
        for a in axes:
            dObj.meta_data.set(a, group[a][:])
            axis_labels.append('.'.join((a, group[a].attrs['units'])))
        dObj.set_axis_labels(*axis_labels)
        self._add_axis_label_meta_data(dObj, group, ordered_axes)

    def _add_patterns(self, dObj, group):
        patterns = group['patterns']
        for key, value in patterns.iteritems():
            dObj.add_pattern(key, core_dims=value['core_dims'],
                             slice_dims=value['slice_dims'])

    def _add_meta_data(self, dObj, group):
        mData = group['meta_data']
        for key, value in mData.iteritems():
            entry = value.name.split('/')[-1]
            dObj.meta_data.set(entry, value.values()[0][:])
