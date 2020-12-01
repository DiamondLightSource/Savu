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
.. module:: multi_nxtomo_loader
   :platform: Unix
   :synopsis: A class for loading multiple standard tomography scans.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import copy
import h5py
import tempfile
from os import path
import numpy as np
import sys
import glob

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.loaders.full_field_loaders.nxtomo_loader import NxtomoLoader
from savu.plugins.utils import register_plugin
from savu.data.data_structures.data_types.stitch_data import StitchData


@register_plugin
class LfovLoader(BaseLoader):
    """
    A class to load 2 scans in Nexus/hdf format into one dataset.

    :param name: The name assigned to the dataset. Default: 'tomo'.
    :param file_name: The shared part of the name of each file\
        (not including .nxs). Default: 'projection'.
    :param data_path: Path to the data inside the \
        file. Default: 'entry/data/data'.
    :param dark: Optional path to the dark field data file, nxs path and \
        scale value. Default: [None, None, 1].
    :param flat: Optional Path to the flat field data file, nxs path and \
        scale value. Default: [None, None, 1].        
    :param order: Order of datasets used for stitching. Default: [1, 0].
    :param row_offset: Offsets of row indices between datasets. Default: [0, -2].
    :param angles: A python statement to be evaluated or a file. Default: None.
    """

    def __init__(self, name='LfovLoader'):
        super(LfovLoader, self).__init__(name)

    def setup(self):
        nxtomo = self._get_nxtomo()
        preview = self.parameters['preview']
        self.shared_name = self.parameters['file_name']
        stitch_dim = 3
        nxtomo.parameters['preview'] = \
            [x for i, x in enumerate(preview) if i != stitch_dim]
        data_obj_list = self._get_data_objects(nxtomo)
        data_obj = \
            self.exp.create_data_object('in_data', self.parameters['name'])

        # dummy file
        filename = path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        stack_or_cat = 'stack'
        data_obj.data = StitchData(data_obj_list, stack_or_cat, stitch_dim)

        if stack_or_cat == 'stack':
            self._setup_4d(data_obj)
            # may want to add this as a parameter...
            self._set_nD_rotation_angle(data_obj_list, data_obj)

        data_obj.set_original_shape(data_obj.data.get_shape())
        self.set_data_reduction_params(data_obj)

    def _get_nxtomo(self):
        nxtomo = NxtomoLoader()
        nxtomo.exp = self.exp
        nxtomo._populate_default_parameters()
        nxtomo.parameters["data_path"] = self.parameters["data_path"]
        nxtomo.parameters["angles"] = self.parameters["angles"]
        return nxtomo

    def _offset_sinogram_index(self, preview, offset):
        if (offset != 0) and len(preview) > 0:
            preview = [idx for idx in preview]
            pre_mod = preview[1]
            if pre_mod == "mid":
                pre_mod = pre_mod + str(offset)
            if (pre_mod != "end") and (pre_mod != ":") and (pre_mod != "mid"):
                try:
                    idx = int(pre_mod)
                    idx = idx + offset
                    pre_mod = str(idx)
                except:
                    names = pre_mod.split(":")
                    if len(names) == 3:
                        step = int(names[2])
                        if step > 1:
                            if "mid" in names[0]:
                                s1 = names[0].split("mid")
                                if s1[-1] == "":
                                    num = offset
                                else:
                                    num = int(s1[-1]) + offset
                                if num > 0:
                                    names[0] = "mid +" + str(num)
                                else:
                                    names[0] = "mid" + str(num)
                            else:
                                num = int(names[0]) + offset
                                if num > 0:
                                    names[0] = "mid +" + str(num)
                                else:
                                    names[0] = "mid" + str(num)

                            if "mid" in names[1]:
                                s1 = names[1].split("mid")
                                if s1[-1] == "":
                                    num = offset
                                else:
                                    num = int(s1[-1]) + offset
                                if num > 0:
                                    names[1] = "mid +" + str(num)
                                else:
                                    names[1] = "mid" + str(num)
                            else:
                                num = int(names[1]) + offset
                                if num > 0:
                                    names[1] = "mid +" + str(num)
                                else:
                                    names[1] = "mid" + str(num)

                            pre_mod = names[0] + ":" + \
                                names[1] + ":" + names[-1]
            preview[1] = pre_mod
        return preview

    def _get_data_objects(self, nxtomo):
        row_offset = self.parameters['row_offset']
        order = self.parameters['order']
        if order[0] < order[-1]:
            order_list = np.arange(order[0], order[1] + 1)
        else:
            order_list = np.arange(order[0], order[1] - 1, -1)
        file_path = copy.copy(self.exp.meta_data.get('data_file'))
        if self.shared_name is None:
            file_list = sorted(glob.glob(file_path + "/*.hdf"))
            if len(file_list) == 0:
                file_list = sorted(glob.glob(file_path + "/*.nxs"))
        else:
            file_list = sorted(
                glob.glob(file_path + "/*" + self.shared_name + "*"))
        if len(order_list) != len(file_list):
            raise ValueError(
                "Number of files found in the folder is not the same as the requested number")
        data_obj_list = []
        dark_folder, dark_key, dark_scale = self.parameters['dark']
        flat_folder, flat_key, flat_scale = self.parameters['flat']
        dark_list = sorted(glob.glob(dark_folder + "/*dark*"))
        flat_list = sorted(glob.glob(flat_folder + "/*flat*"))
        for i in order_list:
            self.exp.meta_data.set('data_file', file_list[i])
            if dark_folder is not None:
                nxtomo.parameters['dark'] = [
                    dark_list[i], dark_key, dark_scale]
            if flat_folder is not None:
                nxtomo.parameters['flat'] = [
                    flat_list[i], flat_key, flat_scale]
            preview = nxtomo.parameters['preview']
            if len(preview) > 0:
                preview = self._offset_sinogram_index(preview, row_offset[i])
            nxtomo.parameters['preview'] = preview
            nxtomo.setup()
            data_obj_list.append(self.exp.index['in_data']['tomo'])
            self.exp.index['in_data'] = {}
        self.exp.meta_data.set('data_file', file_path)
        return data_obj_list

    def _setup_4d(self, data_obj):
        axis_labels = \
            ['rotation_angle.degrees', 'detector_y.pixel', 'detector_x.pixel']

        extra_label = 'scan.number'
        axis_labels.append(extra_label)

        rot = axis_labels.index('rotation_angle.degrees')
        detY = axis_labels.index('detector_y.pixel')
        detX = axis_labels.index('detector_x.pixel')
        extra = axis_labels.index(extra_label)

        data_obj.set_axis_labels(*axis_labels)

        data_obj.add_pattern('PROJECTION', core_dims=(detX, detY),
                             slice_dims=(rot, extra))
        data_obj.add_pattern('SINOGRAM', core_dims=(detX, rot),
                             slice_dims=(detY, extra))

        data_obj.add_pattern('PROJECTION_STACK', core_dims=(detX, detY),
                             slice_dims=(extra, rot))
        data_obj.add_pattern('SINOGRAM_STACK', core_dims=(detX, rot),
                             slice_dims=(extra, detY))

    def _extend_axis_label_values(self, data_obj_list, data_obj):
        dim = 3
        axis_name = data_obj.get_axis_labels()[dim].keys()[0].split('.')[0]

        new_values = np.zeros(data_obj.data.get_shape()[dim])
        inc = len(data_obj_list[0].meta_data.get(axis_name))

        for i in range(len(data_obj_list)):
            new_values[i * inc:i * inc + inc] = \
                data_obj_list[i].meta_data.get(axis_name)

        data_obj.meta_data.set(axis_name, new_values)

    def _set_nD_rotation_angle(self, data_obj_list, data_obj):
        rot_dim_len = data_obj.data.get_shape()[
            data_obj.get_data_dimension_by_axis_label('rotation_angle')]
        new_values = np.zeros([rot_dim_len, len(data_obj_list)])
        for i in range(len(data_obj_list)):
            new_values[:, i] = \
                data_obj_list[i].meta_data.get('rotation_angle')
        data_obj.meta_data.set('rotation_angle', new_values)

    def get_dark_flat_slice_list(self, data_obj):
        slice_list = data_obj._preview._get_preview_slice_list()
        detX_dim = data_obj.get_data_dimension_by_axis_label('detector_x')
        detY_dim = data_obj.get_data_dimension_by_axis_label('detector_y')
        dims = list(set([detX_dim, detY_dim]))
        new_slice_list = []
        for d in dims:
            new_slice_list.append(slice_list[d])
        return new_slice_list
