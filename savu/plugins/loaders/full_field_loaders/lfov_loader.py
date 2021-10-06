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
.. module:: lfov_loader
   :platform: Unix
   :synopsis: Large field-of-view loader. A class for loading 2 standard
    tomography scans.
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import copy
import numpy as np
import glob

import savu.test.test_utils as tu
from savu.plugins.utils import register_plugin
from savu.plugins.loaders.full_field_loaders.multi_nxtomo_loader import \
        MultiNxtomoLoader


@register_plugin
class LfovLoader(MultiNxtomoLoader):

    def __init__(self, name='LfovLoader'):
        super(LfovLoader, self).__init__(name)
        
    def _update_preview(self, preview, offset):
        """
        Add extra sinograms to the preview if there are not enough to stitch
        at least one frame after taking into account the offset between images.

        Parameters
        ----------
        preview : list
            A Savu preview data list.

        Returns
        -------
        None.

        """
        if not offset or not preview:
            return preview
        dObj = self.exp.index['in_data']['tomo']

        # Revert the data shape to before previewing was applied
        dObj.set_shape(dObj.get_original_shape())
        preview = dObj.get_preview().get_integer_entries(preview)
        sino_slice_dim = dObj.get_data_dimension_by_axis_label("detector_y")
        max_sino_idx = dObj.data.shape[sino_slice_dim]
        sl = list(map(int, preview[sino_slice_dim].split(":")))
        sl_0 = sl[0] + offset
        sl_1 = sl[1] + offset
        if (max_sino_idx >= sl_0 >= 0) and (max_sino_idx >= sl_1 >= 0):
            sl[0] = sl_0
            sl[1] = sl_1   
            preview[sino_slice_dim] = ":".join(map(str, sl))
            self.parameters['preview'][sino_slice_dim] = preview[sino_slice_dim]
        return preview

    def _get_order_list(self):
        order = self.parameters['order']
        if order[0] < order[-1]:
            order_list = np.arange(order[0], order[1] + 1)
        else:
            order_list = np.arange(order[0], order[1] - 1, -1)        
        return order_list

    def _get_file_list(self, order_list):
        shared_name = self.parameters["file_name"]
        file_path = copy.copy(self.exp.meta_data.get('data_file'))
        self.exp.meta_data.set('data_file', file_path)
        
        if shared_name is None:
            file_list = self._find_files(file_path, "/*.hdf")
            if len(file_list) == 0:
                file_list = self._find_files(file_path, "/*.nxs")
        else:
            file_list = self._find_files(file_path, "/*" + shared_name + "*")

        if len(order_list) != len(file_list):
            raise ValueError(
                "Number of files found in the folder is not the same as the"
                " requested number")
        return file_list
    
    def _find_files(self, base, name):
        return sorted(glob.glob(base + name)) if base else []

    def _get_data_objects(self, nxtomo):
        order_list = self._get_order_list()
        file_list = self._get_file_list(order_list)        
        dark_folder, dark_key, dark_scale = self.parameters['dark']
        flat_folder, flat_key, flat_scale = self.parameters['flat']
        dark_folder = self.get_conf_path(dark_folder)
        flat_folder = self.get_conf_path(flat_folder)
        dark_list = self._find_files(dark_folder, "/*dark*")
        flat_list = self._find_files(flat_folder, "/*flat*")
        offset = self.parameters['row_offset']
        data_obj_list = []
        for i in order_list:
            self.exp.meta_data.set('data_file', file_list[i])
            # update darks and flats
            if dark_folder is not None:
                nxtomo.parameters['dark'] = [
                    dark_list[i], dark_key, dark_scale]
            if flat_folder is not None:
                nxtomo.parameters['flat'] = [
                    flat_list[i], flat_key, flat_scale]

            nxtomo.setup()
            # update preview
            if offset[i] != 0:
                nxtomo.parameters['preview'] = \
                    self._update_preview(nxtomo.parameters['preview'], offset[i])
            data_obj_list.append(self.exp.index['in_data']['tomo'])
            self.exp.index['in_data'] = {}
        return data_obj_list

    def get_conf_path(self, path):
        # For Savu tests
        if path.split(os.sep)[0] == 'Savu':
            path = tu.get_test_data_path(path.split('/test_data/data/')[1])
        return path
