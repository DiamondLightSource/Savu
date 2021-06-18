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
.. module:: hdf5_template_loader
   :platform: Unix
   :synopsis: A class to load data from a non-standard nexus/hdf5 file using \
   descriptions loaded from a yaml file.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import h5py
import fnmatch
import difflib
import numpy as np

import savu.core.utils as cu
from savu.plugins.utils import register_plugin
from savu.plugins.loaders.yaml_converter import YamlConverter
from savu.data.data_structures.data_types.stitch_data import StitchData


@register_plugin
class Hdf5TemplateLoader(YamlConverter):
    def __init__(self, name='Hdf5TemplateLoader'):
        super(Hdf5TemplateLoader, self).__init__(name)

    def set_data(self, dObj, data):
        path = data['path'] if 'path' in list(data.keys()) else None
        if not path:
            emsg = 'Please specify the path to the data in the h5 file.'
            raise Exception(emsg)

        file_path = self.exp.meta_data.get("data_file") if 'file' not in \
            list(data.keys()) else data['file']
        file_path = self.update_value(dObj, file_path)
        dObj.backing_file = h5py.File(file_path, 'r')

        basename = os.path.basename(path)
        if len(basename.split('*')) > 1:
            return self._stitch_data(dObj, path, data)
        return self._setup_data(dObj, path)

    def _stitch_data(self, dObj, path, data):
        stype, dim = self._get_stitching_info(data)
        remove = data['remove'] if 'remove' in list(data.keys()) else None

        group_name, data_name = os.path.split(path)
        # find all files with the given name
        group = dObj.backing_file.require_group(group_name)
        matches = fnmatch.filter(list(group.keys()), data_name)

        number = []
        for m in matches:
            diff_number = ''
            for diff in difflib.ndiff(m, data_name):
                split = diff.split('- ')
                if len(split) > 1:
                    diff_number += split[-1]
            number.append(int(diff_number))

        matches = [matches[i] for i in np.argsort(number)]
        dObj.data_info.set('wildcard_values', sorted(number))

        data_obj_list = []
        for match in matches:
            match_path = os.path.join(group_name, match)
            sub_obj = self.exp.create_data_object('in_data', match)
            sub_obj.backing_file = dObj.backing_file
            data_obj_list.append(self._setup_data(sub_obj, match_path))
            del self.exp.index['in_data'][match]

        if data_obj_list:
            dObj.data = StitchData(data_obj_list, stype, dim, remove=remove)
            dObj.set_original_shape(dObj.data.get_shape())
        else:
            cu.user_message("The data set %s is empty." % data_name)

        return dObj

    def _get_stitching_info(self, data):
        if 'stack' in list(data.keys()):
            return 'stack', data['stack']
        elif 'cat' in list(data.keys()):
            return 'cat', data['cat']
        else:
            msg = 'Please specify the dimension to stack or concatenate.'
            raise Exception(msg)

    def _setup_data(self, dObj, path):
        path = self.update_value(dObj, path)
        if path in dObj.backing_file:
            dObj.data = dObj.backing_file[self.update_value(dObj, path)]
            dObj.set_shape(dObj.data.shape)
        else:
            raise Exception("The path '%s' was not found in %s" % (path, dObj.backing_file.filename))
        return dObj
