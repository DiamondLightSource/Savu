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
.. module:: min_and_max
   :platform: Unix
   :synopsis: A plugin to calculate the min and max of each frame
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""
import logging
import numpy as np

from scipy.ndimage import gaussian_filter
from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
import savu.core.utils as cu


@register_plugin
class MinAndMax(Plugin, CpuPlugin):

    def __init__(self):
        super(MinAndMax, self).__init__("MinAndMax")

    def circle_mask(self, width, ratio):
        # Create a circle mask.
        mask = np.zeros((width, width), dtype=np.float32)
        center = width // 2
        radius = ratio * center
        y, x = np.ogrid[-center:width - center, -center:width - center]
        mask_check = x * x + y * y <= radius * radius
        mask[mask_check] = 1.0
        return mask

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        in_meta_data = self.get_in_meta_data()[0]
        data = self.get_in_datasets()[0]
        data_shape = data.get_shape()
        width = data_shape[0]
        self.use_mask = self.parameters['masking']
        self.data_pattern = self.parameters['pattern']
        self.mask = np.ones((width, width), dtype=np.float32)
        if self.use_mask is True:
            ratio = self.parameters['ratio']
            if ratio is None:
                try:
                    cor = np.min(in_meta_data.get('centre_of_rotation'))
                    ratio = (min(cor, abs(width - cor))) / (width * 0.5)
                except KeyError:
                    ratio = 1.0
            self.mask = self.circle_mask(width, ratio)
        self.method = self.parameters['method']
        if not (self.method == 'percentile' or self.method == 'extrema'):
            msg = "\n***********************************************\n" \
                  "!!! ERROR !!! -> Wrong method. Please use only one of " \
                  "the provided options \n" \
                  "***********************************************\n"
            logging.warning(msg)
            cu.user_message(msg)
            raise ValueError(msg)
        self.p_min, self.p_max = np.sort(np.clip(np.asarray(
            self.parameters['p_range'], dtype=np.float32), 0.0, 100.0))

    def process_frames(self, data):
        use_filter = self.parameters['smoothing']
        frame = np.nan_to_num(data[0])
        if use_filter is True:
            frame = gaussian_filter(frame, (3, 3))
        if (self.use_mask is True) and (self.data_pattern == 'VOLUME_XZ') \
                and (self.mask.shape == frame.shape):
            frame = frame * self.mask
        if self.method == 'percentile':
            list_out = [np.array(
                [np.percentile(frame, self.p_min)], dtype=np.float32),
                np.array([np.percentile(frame, self.p_max)], dtype=np.float32)]
        else:
            list_out = [np.array([np.min(frame)], dtype=np.float32),
                        np.array([np.max(frame)], dtype=np.float32)]
        return list_out

    def post_process(self):
        in_datasets, out_datasets = self.get_datasets()
        the_min = np.squeeze(out_datasets[0].data[...])
        the_max = np.squeeze(out_datasets[1].data[...])
        pattern = self._get_pattern()
        in_datasets[0].meta_data.set(['stats', 'min', pattern], the_min)
        in_datasets[0].meta_data.set(['stats', 'max', pattern], the_max)

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        try:
            in_pData[0].plugin_data_setup(self._get_pattern(), 'single')
        except:
            msg = "\n***************************************************" \
                  "**********\nCan't find the data pattern: {}.\nThe pattern " \
                  "parameter of this plugin must be relevant to its \n" \
                  "previous plugin\n****************************************" \
                  "*********************\n".format(self._get_pattern())
            logging.warning(msg)
            cu.user_message(msg)
            raise ValueError(msg)

        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        orig_shape = in_dataset[0].get_shape()
        new_shape = (np.prod(np.array(orig_shape)[slice_dirs]), 1)

        labels = ['x.pixels', 'y.pixels']
        for i in range(len(out_datasets)):
            out_datasets[i].create_dataset(shape=new_shape, axis_labels=labels,
                                           remove=True, transport='hdf5')
            out_datasets[i].add_pattern(
                "METADATA", core_dims=(1,), slice_dims=(0,))
            out_pData[i].plugin_data_setup('METADATA', 'single')

    def _get_pattern(self):
        return self.parameters['pattern']

    def nOutput_datasets(self):
        return 2
