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

import json
import h5py
import numpy as np

import savu.plugins.utils as pu
from savu.plugins.utils import register_plugin
from savu.plugins.loaders.base_loader import BaseLoader


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
        self._final_plugin_no = None
        self._start_plugin_no = None

    def setup(self):
        datasets = []
        with h5py.File(self.exp.meta_data.get('data_file'), 'a') as nxsfile:
            datasets = self._read_nexus_file(nxsfile, datasets)         
            datasets = self._set_final_plugin_no(datasets)
            if self.exp.meta_data.get('checkpoint_loader'):
                datasets = self._checkpoint_datasets(datasets)
            else:
                datasets = self._last_unique_datasets(datasets)
            self._create_datasets(nxsfile, datasets, 'in_data')

    def _read_nexus_file(self, nxsfile, datasets):
        # find NXdata
        for key, value in nxsfile.items():
            if self._is_nxdata(value):
                datasets.append(self._get_dataset_info(key, value))
            elif isinstance(value, h5py.Group) and key != 'input_data':
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
            pos = 'final'  # arbitrarily large number
        else:
            name = ''.join(ksplit[2:])
            pos = ksplit[0]
        return {'name': name, 'pos': pos, 'group': value}

    # update this function with information from the Checkpoint class
    def _checkpoint_datasets(self, datasets):
        cp = self.exp.checkpoint
        level, completed_plugins = cp._get_checkpoint_params()
        final_plugin = self.get_final_plugin_no()

        if final_plugin > completed_plugins:
            if level == 'plugin':
                return self._last_unique_datasets(datasets, completed_plugins)
            elif level == 'subplugin':
                out_datasets = [d for d in datasets if d['pos']]  # need key value pair
                out_data_objs = self.create_datasets(f, out_datasets, 'out_data')
                # update experiment datasets for final plugin with out_data_objs
                return self._last_unique_datasets(datasets, completed_plugins)
            else:
                raise Exception("Checkpoint level %s is unknown." % level)
        else:
            return self._last_unique_datasets(datasets)

    def _last_unique_datasets(self, datasets, final=None):
        if final:
            datasets = [d for d in datasets if d['pos'] >= final]
        all_names = list(set([d['name'] for d in datasets]))
        entries = {}
        for n in all_names:
            this_name = [d for d in datasets if d['name'] == n]
            max_pos = np.max(np.array([int(d['pos']) for d in this_name]))
            entries[n] = \
                [d['group'] for d in this_name if int(d['pos']) == max_pos][0]
        return entries

    def _create_datasets(self, nxsfile, datasets, dtype):
        inFile = nxsfile.filename
        data_objs = []
        for name, group in datasets.iteritems():
            dObj = self._create_dataset(name, dtype)
            dObj.backing_file = h5py.File(inFile, 'r')
            dObj.data = self._set_data_type(dObj, group)
            self._read_nexus_group(group, dObj)
            dObj.set_shape(dObj.data.shape)
            self.set_data_reduction_params(dObj)
            data_objs.append(dObj)
        return data_objs

    def _set_data_type(self, dObj, group):
        if 'data_type' not in group:
            return group.get(group.attrs['signal'])
        dObj.data = group['data']
        entry = group['data_type']
        args = self._get_data(entry, 'args')
        args = [a if a != 'self' else dObj for a in args]
        kwargs = self._get_data(entry, 'kwargs')

        cls = str(self._get_data(entry, 'cls'))
        cls_split = cls.split('.')
        cls_inst = \
            pu.load_class('.'.join(cls_split[:-1]), cls_name=cls_split[-1])
        return cls_inst(*args, **kwargs)

    def _get_data(self, entry, key):
        plist = self.exp.meta_data.plugin_list
        if isinstance(entry[key], h5py.Group):
            ddict = {}
            for subkey in entry[key]:
                ddict[subkey] = self._get_data(entry[key], subkey)
            return ddict
        else:
            try:
                value = plist._byteify(json.loads(entry[key][:][0]))
            except:
                value = entry[key][...]
            return value

    def _create_dataset(self, name, dtype):
        return self.exp.create_data_object(dtype, name, override=True)

    def _read_nexus_group(self, group, dObj):
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

    def _set_final_plugin_no(self, datasets):
        nPlugins = max([int(d['pos']) for d in datasets if d['pos'] !=
                        'final'])+1 if datasets else 1
        for d in datasets:
            if d['pos'] == 'final':
                d['pos'] = nPlugins
        self._final_plugin_no = nPlugins - 1
        return datasets

    def get_final_plugin_no(self):
        return self._final_plugin_no
