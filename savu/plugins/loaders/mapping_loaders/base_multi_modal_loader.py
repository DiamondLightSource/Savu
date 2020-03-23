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
.. module:: base_multi_modal_loader
   :platform: Unix
   :synopsis: Contains a base class from which all multi-modal loaders are \
   derived.
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import h5py
import logging

from savu.plugins.loaders.base_loader import BaseLoader


class BaseMultiModalLoader(BaseLoader):
    """
    This class provides a base for all multi-modal loaders
    """

    def __init__(self, name='BaseMultiModalLoader'):
        super(BaseMultiModalLoader, self).__init__(name)
        self._mtype = None

    def multi_modal_setup(self, ltype, data_str, name, patterns=True):
        data_obj = self._get_file_handle(name, ltype)
        NXdef = 'NXstxm' if ltype == 'NXmonitor' else ltype
        entry = self.get_NXapp(NXdef, data_obj.backing_file, 'entry1/')[0]

        path = ('/').join([entry.name, data_str])
        data_obj.data = data_obj.backing_file[path]
        data_obj.set_shape(data_obj.data.shape)
        self._check_for_monitor_data(data_obj, entry)
        self.set_motors(data_obj, entry, 'fluo')
        if patterns:
            self.add_patterns_based_on_acquisition(data_obj, 'fluo')
        return data_obj, entry

    def _get_file_handle(self, name, ltype):
        exp = self.exp
        data_obj = exp.create_data_object("in_data", name)
        data_obj.backing_file = h5py.File(exp.meta_data.get("data_file"), 'r')
        logging.debug("Creating file '%s' '%s'_entry",
                      data_obj.backing_file.filename, ltype)
        return data_obj

    def _check_for_monitor_data(self, data_obj, entry):
        if entry.name + '/monitor/data' in data_obj.backing_file:
            control = data_obj.backing_file[entry.name + '/monitor/data']
            self.exp.meta_data.set('control', control)
            logging.debug('adding the ion chamber to the meta data')
        else:
            logging.warning('No ion chamber information. Leaving this blank')

    def set_motors(self, data_obj, entry, ltype):
        labels = [e.decode("ascii") for e in entry['data'].attrs['axes']]
        motors = [entry['data/' + e] for e in labels]
        units = self._get_attrs(motors, 'units', 'unit')
        self._mtype = self._get_attrs(motors, 'transformation_type', 'None')
        self._set_axis_labels(data_obj, motors, labels, units)

    def _get_attrs(self, entries, key, default):
        return [e.attrs[key].decode("ascii") if key in list(e.attrs.keys()) else
                default for e in entries]

    def _set_axis_labels(self, dObj, motors, labels, units):
        trans = self.get_motor_dims('translation')
        rot_dim = self._mtype.index('rotation')
        angles = motors[rot_dim][()]
        labels[rot_dim] = 'rotation_angle'
        self._set_meta_data(dObj, 'rotation_angle', angles)
        if trans:
            self._set_meta_data(dObj, 'x', motors[trans[-1]][()])
            labels[trans[-1]] = 'x'
            if len(trans) > 1:
                self._set_meta_data(dObj, 'y', motors[trans[-2]][()])
                labels[trans[-2]] = 'y'
        labels = [labels[i] + '.' + units[i] for i in range(len(labels))]
        dObj.set_axis_labels(*tuple(labels))

    def _set_meta_data(self, dObj, key, value):
        value = value[:, 0] if value.ndim > 1 else value
        dObj.meta_data.set(key, value)

    def get_motor_dims(self, key):
        return [i for i in range(len(self._mtype)) if self._mtype[i] == key]

    def add_patterns_based_on_acquisition(self, data_obj, ltype):
        dims = list(range(len(self._mtype)))

        proj_dims = tuple(self.get_motor_dims('translation'))
        if proj_dims:
            data_obj.add_pattern("PROJECTION", core_dims=proj_dims,
                                 slice_dims=tuple(set(dims) - set(proj_dims)))

        rot_dim = tuple(self.get_motor_dims('rotation'))
        if rot_dim:
            sino_dir = rot_dim + (proj_dims[-1],) if proj_dims else rot_dim
            sino_slice_dir = tuple(set(dims) - set(sino_dir))
            data_obj.add_pattern("SINOGRAM", core_dims=sino_dir,
                                 slice_dims=sino_slice_dir)
