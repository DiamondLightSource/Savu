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

from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.corrections.base_correction import BaseCorrection
from savu.plugins.utils import register_plugin


@register_plugin
class TimeBasedCorrection(BaseCorrection, CpuPlugin):
    """
    Apply a time-based dark and flat field correction to data.

    :param in_range: Set to True if you require values in the \
        range [0, 1]. Default: False.
    """

    def __init__(self, name="TimeBasedCorrection"):
        super(TimeBasedCorrection, self).__init__(name)

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        pData = self.get_plugin_in_datasets()[0]
        self.proj_dim = inData.find_axis_label_dimension('rotation_angle')
        self.slice_dir = pData.get_slice_dimension()
        nDims = len(pData.get_shape())
        self.sslice = [slice(None)]*nDims
        # get data image key
        self.data_idx = inData.data.get_index(0)

        # calculate dark and flat averages
        self.dark, self.dark_idx = \
            self.calc_average(inData.data.dark(), inData.data.get_index(2))
        self.flat, self.flat_idx = \
            self.calc_average(inData.data.flat(), inData.data.get_index(1))

        inData.meta_data.set('multiple_dark', self.dark)
        inData.meta_data.set('multiple_flat', self.flat)

    def calc_average(self, data, key):
        idx = np.where(np.diff(key) > 1)[0]
        start = [0] + list(idx+1)
        # get relative and absolute indexes of requested data
        rel_idx = zip(start, start[1:] + [len(key)])
        abs_idx = zip(key[np.append(0, idx+1)], np.append(key[idx], key[-1])+1)
        mean_range = [np.arange(*i) for i in rel_idx]
        sl = np.array([[slice(None)]*3]*len(mean_range))
        sl[:, self.proj_dim] = mean_range
        sl = [list(s) for s in sl]
        return [np.mean(data[sl[i]], axis=0) for i in range(len(sl))], abs_idx

    def process_frames(self, data):
        data = data[0]
        frames = self._get_frames()
        output = np.empty(data.shape, dtype=np.float32)
        nSlices = data.shape[self.slice_dir]
        for i in range(nSlices):
            self.sslice[self.slice_dir] = i
            proj = data[tuple(self.sslice)]
            flat = self.calculate_flat_field(
                frames[i], proj, *self.find_nearest_frames(
                    self.flat_idx, frames[i]))
            dark = self.calculate_dark_field(
                *self.find_nearest_frames(self.dark_idx, frames[i]))

            if self.parameters['in_range']:
                proj = self.in_range(proj, flat)
            # perform correction
            output[self.sslice] = np.nan_to_num((proj-dark)/(flat-dark))
        return output

    def in_range(self, data, flat):
        data[data > flat] = flat[data > flat]
        return data

    def _get_frames(self):
        frames = self.get_current_slice_list()[0][self.slice_dir]
        frames = range(frames.start, frames.stop, frames.step)
        inData = self.get_in_datasets()[0]
        return inData.data.get_index(0, full=True)[np.array(frames)]

    def find_nearest_frames(self, idx_list, value):
        """ Find the index of the two entries that 'value' lies between in \
            'idx_list' and calculate the distance between each of them.
        """
        start_array = np.array([idx_list[i][0] for i in range(len(idx_list))])
        end_array = np.array([idx_list[i][1] for i in range(len(idx_list))])
        idx = (np.abs(start_array - value)).argmin()
        idx2 = idx+1 if start_array[idx] < value else idx-1
        nearest = list(set([idx, idx2]))
        rrange = [end_array[nearest[0]]-1, start_array[nearest[1]]]
        length = float(rrange[1] - rrange[0])
        distance = [(value - rrange[0])/length, (rrange[1] - value)/length]
        return nearest, distance

    def calculate_flat_field(self, frame, data, frames, distance):
        return self.flat[frames[0]]*distance[0] + \
            self.flat[frames[1]]*distance[1]

    def calculate_dark_field(self, frames, distance):
        return self.dark[frames[0]]*distance[0] + \
            self.dark[frames[1]]*distance[1]
