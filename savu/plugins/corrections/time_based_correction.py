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
.. module:: time_based_correction
   :platform: Unix
   :synopsis: A time-based dark and flat field correction using linear\
       interpolation

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
np.seterr(divide='ignore', invalid='ignore')

from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.corrections.base_correction import BaseCorrection
from savu.plugins.utils import register_plugin


@register_plugin
class TimeBasedCorrection(BaseCorrection, CpuPlugin):

    def __init__(self, name="TimeBasedCorrection"):
        super(TimeBasedCorrection, self).__init__(name)

    def pre_process(self):
        self.count = 0
        inData = self.get_in_datasets()[0]
        pData = self.get_plugin_in_datasets()[0]
        self.mfp = inData._get_plugin_data()._get_max_frames_process()
        self.proj_dim = \
            inData.get_data_dimension_by_axis_label('rotation_angle')
        self.slice_dir = pData.get_slice_dimension()
        nDims = len(pData.get_shape())
        self.sslice = [slice(None)]*nDims

        self.image_key = inData.data.get_image_key()
        changes = np.where(np.diff(self.image_key) != 0)[0] + 1
        self.split_key = np.split(self.image_key, changes)
        self.split_idx = np.split(np.arange(len(self.image_key)), changes)
        self.data_key = inData.data.get_index(0)

        self.dark, self.dark_idx = self.calc_average(inData.data.dark(), 2)
        self.flat, self.flat_idx = self.calc_average(inData.data.flat(), 1)

        inData.meta_data.set('multiple_dark', self.dark)
        inData.meta_data.set('multiple_flat', self.flat)

    def calc_average(self, data, key):
        im_key = np.where(self.image_key == key)[0]
        splits = np.where(np.diff(im_key) > 1)[0]+1
        local_idx = np.split(np.arange(len(im_key)), splits)
        mean_data = [np.mean(data[np.array(local_idx[i])], axis=0)
                     for i in range(len(local_idx))]
        list_idx = list(np.where([key in i for i in self.split_key])[0])
        return mean_data, list_idx

    def process_frames(self, data):
        proj = data[0]
        frame = self.get_global_frame_index()[self.count]
        flat = self.calculate_flat_field(frame, proj,
                *self.find_nearest_frames(self.flat_idx, frame))
        dark = self.calculate_dark_field(frame, proj,
                *self.find_nearest_frames(self.dark_idx, frame))

        if self.parameters['in_range']:
            proj = self.in_range(proj, flat)

        self.count += 1
        return np.nan_to_num((proj-dark)/(flat-dark))

    def in_range(self, data, flat):
        data[data > flat] = flat[data > flat]
        return data

    def find_nearest_frames(self, idx_list, value):
        """ Find the index of the two entries that 'value' lies between in \
            'idx_list' and calculate the distance between each of them.
        """
        global_val = self.data_key[value]
        # find which list (index) global_val belongs to
        list_idx = [global_val in i for i in self.split_idx].index(True)
        val_list = self.split_idx[list_idx]
        # find length of list
        length_list = len(val_list)
        # find position of global_val in list and distance from each end
        pos = np.where(val_list == global_val)[0][0]
        dist = [(length_list-pos)/float(length_list), pos/float(length_list)]

        # find closest before and after idx_list entries
        new_list = list(np.sort(np.append(idx_list, list_idx)))
        new_idx = new_list.index(list_idx)

        entry1 = new_idx-1 if new_idx != 0 else new_idx+1
        entry2 = new_idx+1 if new_idx != len(new_list)-1 else new_idx-1
        before = idx_list.index(new_list[entry1])
        after = idx_list.index(new_list[entry2])

        return [before, after], dist

    def calculate_flat_field(self, frame, data, frames, distance):
        return self.flat[frames[0]]*distance[0] + \
            self.flat[frames[1]]*distance[1]

    def calculate_dark_field(self, frame, data, frames, distance):
        return self.dark[frames[0]]*distance[0] + \
            self.dark[frames[1]]*distance[1]

    def get_max_frames(self):
        return 'single'
