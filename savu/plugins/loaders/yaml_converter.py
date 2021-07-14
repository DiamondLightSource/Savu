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
.. module:: yaml_converter
   :platform: Unix
   :synopsis: 'A class to load data from a non-standard nexus/hdf5 file using \
               descriptions loaded from a yaml file.'

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import h5py
import yaml
import copy
import logging
import collections.abc as collections
import numpy as np  # used in exec so do not delete
from ast import literal_eval

import savu.plugins.utils as pu
import savu.plugins.loaders.utils.yaml_utils as yu
from savu.plugins.loaders.base_loader import BaseLoader
from savu.data.experiment_collection import Experiment


class YamlConverter(BaseLoader):
    def __init__(self, name='YamlConverter'):
        super(YamlConverter, self).__init__(name)

    def setup(self, template=False, metadata=True):
        #  Read YAML file
        yfile = self.parameters['yaml_file']
        data_dict = yu.read_yaml(self._get_yaml_file(yfile))
        data_dict = self._check_for_inheritance(data_dict, {})
        self._check_for_imports(data_dict)
        data_dict.pop('inherit', None)
        data_dict.pop('import', None)
        if template:
            return data_dict

        data_dict = self._add_template_updates(data_dict)
        self._set_entries(data_dict)

    def _get_yaml_file(self, yaml_file):
        if yaml_file is None:
            raise Exception('Please pass a yaml file to the yaml loader.')
            
        # try the absolute path
        yaml_abs = os.path.abspath(yaml_file)
        if os.path.exists(yaml_abs):
            return yaml_abs
        
        # try adding the path to savu
        if len(yaml_file.split('Savu/')) > 1:
            yaml_savu = os.path.join(os.path.dirname(__file__), "../../../",
                                     yaml_file.split('Savu/')[1])
            if os.path.exists(yaml_savu):
                return yaml_savu

        # try adding the path to the templates folder
        yaml_templ = os.path.join(os.path.dirname(__file__), yaml_file)
        if os.path.exists(yaml_templ):
            return yaml_templ

        raise Exception('The yaml file does not exist %s' % yaml_file)

    def _add_template_updates(self, ddict):
        all_entries = ddict.pop('all', {})
        for key, value in all_entries:
            for entry in ddict:
                if key in list(entry.keys()):
                    entry[key] = value

        for entry in self.parameters['template_param']:
            updates = self.parameters['template_param'][entry]
            ddict[entry]['params'].update(updates)
        return ddict

    def _check_for_imports(self, ddict):
        if 'import' in list(ddict.keys()):
            for imp in ddict['import']:
                name = False
                if len(imp.split()) > 1:
                    imp, name = imp.split('as')
                mod = __import__(imp.strip())
                globals()[mod.__name__ if not name else name] = mod

    def _check_for_inheritance(self, ddict, inherit, override=False):
        if 'inherit' in list(ddict.keys()):
            idict = ddict['inherit']
            idict = idict if isinstance(idict, list) else [idict]
            for i in idict:
                if i != 'None':
                    new_dict = yu.read_yaml(self._get_yaml_file(i))
                    new_dict, isoverride = \
                        self.__override(inherit, new_dict, override)
                    inherit.update(new_dict)
                    inherit = self._check_for_inheritance(
                            new_dict, inherit, override=isoverride)
        self._update(inherit, ddict)
        return inherit

    def __override(self, inherit, ddict, override):
        isoverride = False
        if 'override' in ddict:
            isoverride = ddict.pop('override')
        if override:
            for old, new in override.items():
                ddict[new] = ddict.pop(old)
                if new in list(inherit.keys()):
                    self._update(ddict[new], inherit[new])
        return ddict, isoverride

    def _update(self, d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = self._update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def _set_entries(self, ddict):
        entries = list(ddict.keys())
        for name in entries:
            self.get_description(ddict[name], name)

    def get_description(self, entry, name, metadata=True):
        # set params first as we may need them subsequently
        if 'params' in entry:
            self._set_params(entry['params'])
        # --------------- check for data entry -----------------------------
        if 'data' in list(entry.keys()):
            data_obj = self.exp.create_data_object("in_data", name)
            data_obj = self.set_data(data_obj, entry['data'])
            
        else:
            emsg = 'Please specify the data information in the yaml file.'
            raise Exception(emsg)

        if metadata:
            self._get_meta_data_descriptions(entry, data_obj)

    def _get_meta_data_descriptions(self, entry, data_obj):
        # --------------- check for axis label information -----------------
        if 'axis_labels' in list(entry.keys()):
            self._set_axis_labels(data_obj, entry['axis_labels'])
        else:
            raise Exception('Please specify the axis labels in the yaml file.')

        # --------------- check for data access patterns -------------------
        if 'patterns' in list(entry.keys()):
            self._set_patterns(data_obj, entry['patterns'])
        else:
            raise Exception('Please specify the patterns in the yaml file.')

        # add any additional metadata
        if 'metadata' in entry:
            self._set_metadata(data_obj, entry['metadata'])
        self.set_data_reduction_params(data_obj)

        if 'exp_metadata' in entry:
            self._set_metadata(data_obj, entry['exp_metadata'], exp=True)

    def set_data(self, name, entry):
        raise NotImplementedError('Please implement "set_data" function'
                                  ' in the loader')

    def _set_keywords(self, dObj):
        filepath = str(dObj.backing_file.filename)
        shape = str(dObj.get_shape())
        return {'dfile': filepath, 'dshape': shape}

    def __get_wildcard_values(self, dObj):
        if 'wildcard_values' in list(dObj.data_info.get_dictionary().keys()):
            return dObj.data_info.get('wildcard_values')
        return None

    def update_value(self, dObj, value, itr=0):
        import pdb
        # setting the keywords
        if dObj is not None:
            dshape = dObj.get_shape()
            dfile = dObj.backing_file
            globals()['dfile'] = dfile
            wildcard = self.__get_wildcard_values(dObj)

        if isinstance(value, str):
            split = value.split('$')
            if len(split) > 1:
                value = self._convert_string(dObj, split[1])
                try:
                    value = eval(value, globals(), locals())
                    value = self._convert_bytes(value)
                except Exception as e:
                    msg = (f"Error evaluating value: '{value}' \n %s" % e)
                    try:
                        value = value.replace("index(", "index(b")
                        value = eval(value, globals(), locals())
                        value = self._convert_bytes(value)
                    except:
                        raise Exception(msg)
        return value

    def _convert_string(self, dObj, string):
        for old, new in self.parameters.items():
            if old in string:
                if isinstance(new, str):
                    split = new.split('$')
                    if len(split) > 1:
                        new = split[1]
                    elif isinstance(new, str): # nothing left to split
                        new = "'%s'" % new
                string = self._convert_string(
                        dObj, string.replace(old, str(new)))
        return string

    def _convert_bytes(self, value):
        # convert bytes to str - for back compatability
        if isinstance(value, bytes):
            return value.decode("ascii")
        if isinstance(value, np.ndarray) and isinstance(value[0], bytes):
            return value.astype(str)
        return value

    def _set_params(self, params):
        # Update variable parameters that are revealed in the template
        params = self._update_template_params(params)
        self.parameters.update(params)
        # find files, open and add to the namespace then delete file params
        files = [k for k in list(params.keys()) if k.endswith('file')]
        for f in files:
            param = params[f]
            try:
                globals()[str(f)] = self.update_value(None, param)
            except IOError:
                self._check_for_test_data(f, param)
            del params[f]

    def _check_for_test_data(self, f, param):
        # check if this is Savu test data
        substrs = param.split("'")[1:2]
        filename = None
        for s in substrs:
            try:
                filename = self._get_yaml_file(s)
                break
            except:
                pass
        param = param.replace(s, filename)
        globals()[str(f)] = self.update_value(None, param)
        del self.parameters[f]

    def _update_template_params(self, params):
        for k, v in params.items():
            v = pu.is_template_param(v)
            if v is not False:
                params[k] = \
                    self.parameters[k] if k in list(self.parameters.keys()) else v[1]
        return params

    def _set_axis_labels(self, dObj, labels):
        dims = list(range(len(list(labels.keys()))))
        axis_labels = [None]*len(list(labels.keys()))
        for d in dims:
            self._check_label_entry(labels[d])
            l = labels[d]
            for key in list(l.keys()):
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
        for key, dims in patterns.items():
            core_dims = self.__get_tuple(
                    self.update_value(dObj, dims['core_dims']))
            slice_dims = self.__get_tuple(
                    self.update_value(dObj, dims['slice_dims']))
            dObj.add_pattern(key, core_dims=core_dims, slice_dims=slice_dims)

    def __get_tuple(self, val):
        return literal_eval(val) if not isinstance(val, tuple) else val

    def _set_metadata(self, dObj, mdata, exp=False):
        populate = dObj.exp if exp else dObj
        for key, value in mdata.items():
            value = self.update_value(dObj, value['value'])
            populate.meta_data.set(key, value)
