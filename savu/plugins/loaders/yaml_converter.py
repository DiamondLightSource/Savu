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
.. module:: yaml_loader
   :platform: Unix
   :synopsis: A class to load data from a non-standard nexus/hdf5 file using \
   descriptions loaded from a yaml file.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import yaml
import collections
import numpy as np # used in exec so do not delete
from collections import OrderedDict
from savu.plugins.loaders.base_loader import BaseLoader


class YamlConverter(BaseLoader):
    """
    A class to load data from a non-standard nexus/hdf5 file using \
    descriptions loaded from a yaml file.

    :u*param yaml_file: Path to the file containing the data \
        descriptions. Default: None.
    """

    def __init__(self, name='YamlConverter'):
        super(YamlConverter, self).__init__(name)

    def setup(self):
        #  Read YAML file
        if self.parameters['yaml_file'] is None:
            raise Exception('Please pass a yaml file to the yaml loader.')

        data_dict = self._read_yaml(self.parameters['yaml_file'])
        data_dict = self._check_for_inheritance(data_dict, {})
        self._check_for_imports(data_dict)
        self._set_entries(data_dict)

    def _read_yaml(self, path):
        with open(path, 'r') as stream:
            data_dict = self.ordered_load(stream, yaml.SafeLoader)
        return data_dict

    def _check_for_imports(self, ddict):
        if 'import' in ddict.keys():
            for imp in ddict['import']:
                name = False
                if len(imp.split()) > 1:
                    imp, name = imp.split('as')
                mod = __import__(imp.strip())
                globals()[mod.__name__ if not name else name] = mod

        for key, value in globals().iteritems():
            print "print the globals dict", key, value

    def _check_for_inheritance(self, ddict, inherit):
        if 'inherit' in ddict.keys():
            idict = ddict['inherit']
            idict = idict if isinstance(idict, list) else [idict]
            for i in idict:
                if i != 'None':
                    new_dict = self._read_yaml(i)
                    inherit.update(new_dict)
                    inherit = self._check_for_inheritance(new_dict, inherit)
        self._update(inherit, ddict)
        return inherit

    def _update(self, d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                d[k] = self._update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def _set_entries(self, ddict):
        ddict.pop('inherit', None)
        ddict.pop('import', None)
        entries = ddict.keys()
        for name in entries:
            self.get_description(ddict[name], name)

    def get_description(self, entry, name):
        # set params first as we may need them subsequently
        if 'params' in entry:
            self._set_params(entry['params'])

        # --------------- check for data entry -----------------------------
        if 'data' in entry.keys():
            data_obj = self.set_data(name, entry['data'])
        else:
            emsg = 'Please specify the data information in the yaml file.'
            raise Exception(emsg)

        # --------------- check for axis label information -----------------
        if 'axis_labels' in entry.keys():
            self._set_axis_labels(data_obj, entry['axis_labels'])
        else:
            raise Exception('Please specify the axis labels in the yaml file.')

        # --------------- check for data access patterns -------------------
        if 'patterns' in entry.keys():
            self._set_patterns(data_obj, entry['patterns'])
        else:
            raise Exception('Please specify the patterns in the yaml file.')

        # add any additional metadata
        if 'metadata' in entry:
            self._set_metadata(data_obj, entry['metadata'])
        self.set_data_reduction_params(data_obj)

    def set_data(name, entry):
        raise NotImplementedError('Please implement "get_description" function'
                                  'in the loader')

    def _set_keywords(self, dObj):
        filepath = str(dObj.backing_file.filename)
        shape = str(dObj.get_shape())
        return {'dfile': filepath, 'dshape': shape}

    def update_value(self, dObj, value):
        # setting the keywords
        dshape = dObj.get_shape()
        dfile = dObj.backing_file
        if isinstance(value, str):
            split = value.split('$')
            if len(split) > 1:
                value = self._convert_string(dObj, split[1])
                exec('value = ' + value)
        return value

    def _convert_string(self, dObj, string):
        for old, new in self.parameters.iteritems():
            if old in string:
                print "replacing ", old, "with", new
                if isinstance(new, str):
                    split = new.split('$')
                    if len(split) > 1:
                        new = split[1]
                    elif isinstance(new, str):
                        new = "'%s'" % new
                string = self._convert_string(
                        dObj, string.replace(old, str(new)))
        return string

    def _set_params(self, params):
        # find files
        files = [k for k in params.keys() if k.endswith('file')]
        # Open and add to the namespace then delete file params
        thefile = None
        for f in files:
            exec("thefile = " + params[f].split('$')[-1])
            globals()[str(f)] = thefile
            del params[f]
        self.parameters.update(params)

    def _set_axis_labels(self, dObj, labels):
        dims = range(len(labels.keys()))
        axis_labels = [None]*len(labels.keys())
        for d in dims:
            self._check_label_entry(labels[d])
            l = labels[d]
            for key in l.keys():
                l[key] = self.update_value(dObj, l[key])
            axis_labels[l['dim']] = (l['name'] + '.' + l['units'])
            if l['value'] is not None:
                dObj.meta_data.set(l['name'], l['value'])
        dObj.set_axis_labels(*axis_labels)

    def _check_label_entry(self, label):
        required = ['dim', 'name', 'value', 'units']
        try:
            [label[i] for i in required]
        except:
            raise Exception("name, value and units are required fields for \
                            axis labels")

    def _set_patterns(self, dObj, patterns):
        for key, dims in patterns.iteritems():
            core_dims = self.update_value(dObj, dims['core_dims'])
            slice_dims = self.update_value(dObj, dims['slice_dims'])
            dObj.add_pattern(key, core_dims=core_dims, slice_dims=slice_dims)

    def _set_metadata(self, dObj, mdata):
        for key, value in mdata.iteritems():
            value = self.update_value(dObj, value['value'])
            dObj.meta_data.set(key, value)

    def ordered_load(self, stream, Loader=yaml.Loader,
                     object_pairs_hook=OrderedDict):
        class OrderedLoader(Loader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return object_pairs_hook(loader.construct_pairs(node))
        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)
