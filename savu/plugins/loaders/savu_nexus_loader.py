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
.. module:: savu_nexus_loader
   :platform: Unix
   :synopsis: A class for loading savu output data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import json
import h5py
import copy
import numpy as np

import savu.plugins.utils as pu
import savu.core.utils as cu
from savu.plugins.utils import register_plugin
from savu.plugins.loaders.base_loader import BaseLoader

from savu.core.utils import ensure_string


@register_plugin
class SavuNexusLoader(BaseLoader):
    def __init__(self, name='SavuNexusLoader'):
        super(SavuNexusLoader, self).__init__(name)
        self._all_preview_params = None

    def setup(self):
        self._all_preview_params = copy.deepcopy(self.parameters['preview'])

        datasets = []
        with h5py.File(self.exp.meta_data.get('data_file'), 'r') as nxsfile:
            datasets = self._read_nexus_file(nxsfile, datasets)
            datasets = self._update_plugin_numbers(datasets)

            exp_dict = self.exp.meta_data.get_dictionary()
            if 'checkpoint_loader' in list(exp_dict.keys()):
                self.__checkpoint_reload(nxsfile, datasets)
            else:
                self.__reload(nxsfile, datasets)

    def __reload(self, nxsfile, datasets):
        if self.parameters['datasets']:
            datasets = self.__get_parameter_datasets(datasets)
        else:
            datasets = self._last_unique_datasets(datasets)
        self._create_datasets(nxsfile, datasets, 'in_data')

    def __checkpoint_reload(self, nxsfile, datasets):
        cp = self.exp.checkpoint
        level, completed_plugins = cp._get_checkpoint_params()
        datasets = self._last_unique_datasets(datasets, completed_plugins+1)
        self._create_datasets(nxsfile, datasets, 'in_data')

        # update input data meta data
        for name in list(self.exp.index['in_data'].keys()):
            self.__update_metadata('in_data', name)

        if level == 'subplugin':
            # update output data meta data
            for name in list(self.exp.index['out_data'].keys()):
                self.__update_metadata('out_data', name)

    def __get_parameter_datasets(self, datasets):
        param_datasets = self.parameters['datasets']
        names = self.parameters['names'] if self.parameters['names'] else None
        if names and len(names) != len(param_datasets):
            raise Exception('Please enter a name for each dataset.')

        subset = {}
        found = []
        for i, p in enumerate(param_datasets):
            for d in datasets:
                if p in d['group'].name:
                    found.append(p)
                    name = names[i] if names else d['name']
                    subset[name] = d['group']

        missing = set(param_datasets).difference(set(found))
        if missing:
            msg = "Cannot find the dataset %s in the input nexus file." \
                % missing
            raise Exception(msg)

        if len(subset) != len(param_datasets):
            msg = "Multiple datasets with the same name cannot co-exist."
            raise Exception(msg)

        return subset

    def __update_metadata(self, dtype, name):
        cp = self.exp.checkpoint
        if name in cp.meta_data.get(dtype):
            new_dict = cp.meta_data.get([dtype, name])
            self.exp.index[dtype][name].meta_data._set_dictionary(new_dict)

    def _read_nexus_file(self, nxsfile, datasets):
        # find NXdata
        for key, value in nxsfile.items():
            if self._is_nxdata(value):
                datasets.append(self._get_dataset_info(key, value))
            elif isinstance(value, h5py.Group) and key not in ['input_data', 'entry1']:     #ignore groups called 'input_data' or 'entry1'
                self._read_nexus_file(value, datasets)
        return datasets

    def _is_nxdata(self, value):
        check = 'NX_class' in value.attrs.keys() and ensure_string(value.attrs['NX_class']) == 'NXdata'
        return check

    def _get_dataset_info(self, key, value):
        import unicodedata
        key = unicodedata.normalize('NFKD', key)
        ksplit = key.split('-')

        if len(ksplit) == 1 and ''.join(key.split('_')[0:2]) == 'finalresult':
            name = '_'.join(key.split('_')[2:])
            pos = 'final'
        else:
            name = ''.join(ksplit[2:])
            pos = ksplit[0]
        return {'name': name, 'pos': pos, 'group': value}

    def _last_unique_datasets(self, datasets, final=None, names=None):
        if final:
            datasets = [d for d in datasets if int(d['pos']) < final]

        all_names = list(set([d['name'] for d in datasets]))
        names = [n for n in all_names if n in names] if names else all_names
        entries = {}
        for n in names:
            this_name = [d for d in datasets if d['name'] == n]
            max_pos = np.max(np.array([int(d['pos']) for d in this_name]))
            entries[n] = \
                [d['group'] for d in this_name if int(d['pos']) == max_pos][0]
        return entries

    def _create_datasets(self, nxsfile, datasets, dtype):
        data_objs = []

        for name, group in datasets.items():
            self.__set_preview_params(name)
            dObj = self._create_dataset(name, dtype)
            self._set_data_type(dObj, group, nxsfile.filename)
            self._read_nexus_group(group, dObj)
            dObj.set_shape(dObj.data.shape)
            self.__apply_previewing(dObj)
            data_objs.append(dObj)
        return data_objs

    def __set_preview_params(self, name):
        if isinstance(self._all_preview_params, dict):
            self.parameters['preview'] = self._all_preview_params[name] if \
                name in list(self._all_preview_params.keys()) else []

    def _set_data_type(self, dObj, group, nxs_filename):
        link = group.get(group.attrs['signal'], getlink=True)
        if isinstance(link, h5py._hl.group.HardLink) and \
                self.exp.meta_data.get('test_state') is True:
            link.filename = nxs_filename
            link.path = group.name + '/data'

        fname = os.path.join(os.path.dirname(nxs_filename), link.filename)

        dObj.backing_file = h5py.File(fname, 'r')
        dObj.data = dObj.backing_file[link.path]

        if 'data_type' not in group:
            return

        entry = group['data_type']
        args = self._get_data(entry, 'args')
        args = [args[''.join(['args', str(i)])] for i in range(len(args))]
        args = [a if a != 'self' else dObj for a in args]
        kwargs = self._get_data(entry, 'kwargs')
        extras = self._get_data(entry, 'extras')

        cls = str(self._get_data(entry, 'cls'))
        cls_split = cls.split('.')
        cls_inst = \
            pu.load_class('.'.join(cls_split[:-1]), cls_name=cls_split[-1])
        dObj.data = cls_inst(*args, **kwargs)
        dObj.data._base_post_clone_updates(dObj.data, extras)

    def _get_data(self, entry, key):
        if isinstance(entry[key], h5py.Group):
            ddict = {}
            for subkey in entry[key]:
                ddict[subkey] = self._get_data(entry[key], subkey)
            return ddict
        else:
            try:
                value = json.loads(entry[key][()][0])
            except Exception:
                value = cu._savu_decoder(entry[key][()])
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
        axis_labels = []

        for ax in axes:
            ax = ensure_string(ax)
            ordered_axes[group.attrs['_'.join((ax, 'indices'))]] = ax
            dObj.meta_data.set(ax, group[ax][:])
            units = ensure_string(group[ax].attrs['units'])
            axis_labels.append('.'.join((ax, units)))

        dObj.set_axis_labels(*axis_labels)

    def _add_patterns(self, dObj, group):
        patterns = group['patterns']
        for key, value in patterns.items():
            dObj.add_pattern(key, core_dims=value['core_dims'],
                             slice_dims=value['slice_dims'])

    def _add_meta_data(self, dObj, group):
        def get_meta_data_entries(name, obj):
            for key, val in obj.attrs.items():
                if val == 'NXdata':
                    dObj.meta_data.set(name.split('/'), list(obj.values())[0][...])
        group['meta_data'].visititems(get_meta_data_entries)

    def _update_plugin_numbers(self, datasets):
        all_names = list(set([d['name'] for d in datasets]))
        updated = []
        for n in all_names:
            this = [d for d in datasets if d['name'] == n]
            p_numbers = [int(d['pos']) for d in this if d['pos'] != 'final']
            nPlugins = max(p_numbers)+1 if this and p_numbers else 1
            for d in this:
                if d['pos'] == 'final':
                    d['pos'] = nPlugins
            updated.extend(this)
        return datasets

    def __apply_previewing(self, dObj):
        preview = self._all_preview_params
        if isinstance(preview, dict):
            name = dObj.get_name()
            if name in list(self._all_preview_params.keys()):
                self.parameters['preview'] = self._all_preview_params[name]
        self.set_data_reduction_params(dObj)
