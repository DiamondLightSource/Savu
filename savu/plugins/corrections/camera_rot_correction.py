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
.. module:: camera_rot_correction
   :platform: Unix
   :synopsis: A plugin to apply a rotation to projection images
.. moduleauthor:: Malte Storm<malte.storm@diamond.ac.uk>
"""

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from skimage.transform import rotate
import numpy as np


@register_plugin
class CameraRotCorrection(BaseFilter, CpuPlugin):

    def __init__(self):
        super(CameraRotCorrection, self).__init__("CameraRotCorrection")

    def pre_process(self):
        pass

    def process_frames(self, data):
        return rotate(data[0].astype(np.float64),
                      self.parameters['angle'], center=self.centre,
                      mode='reflect')[tuple(self.new_slice)]

    def post_process(self):
        pass

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', 'single')
        det_y = in_dataset[0].get_data_dimension_by_axis_label('detector_y')
        det_x = in_dataset[0].get_data_dimension_by_axis_label('detector_x')

        self.shape = list(in_dataset[0].get_shape())
        self.core_dims = in_pData[0].get_core_dimensions()

        self.use_auto_centre = self.parameters['use_auto_centre']
        self.angle = self.parameters['angle']
        self.static_crop = self.parameters['crop_edges']
        self.auto_crop = self.parameters['auto_crop']

        if self.auto_crop and isinstance(self.angle, list):
            plugin = self.__class__.__name__
            msg = "Parameter tuning on the angles in %s plugin is only " \
                  "possible with auto_crop set to False." % plugin
            raise Exception(msg)

        img_dims = self.get_in_datasets()[0].get_shape()
        if self.use_auto_centre:
            self.centre = (
            img_dims[det_y] // 2 - 0.5 * np.mod(img_dims[det_y], 2),
            img_dims[det_x] // 2 - 0.5 * np.mod(img_dims[det_x], 2))
        else:
            self.centre = (
            self.parameters['centre_y'], self.parameters['centre_x'])

        # If the data is cropped then the centre of rotation must be shifted
        # accordingly, e.g if preview is [:, a:b, c:d] then shift is (a, c)
        shift = self.exp.meta_data.get(
            in_dataset[0].get_name() + '_preview_starts')
        self.centre = (
        self.centre[0] - shift[det_y], self.centre[1] - shift[det_x])

        self.new_slice = [slice(None)] * 2
        img_dims = self.get_in_datasets()[0].get_shape()

        if self.static_crop > 0 and not self.auto_crop:
            self.new_slice = [
                slice(self.static_crop, img_dims[det_y] - self.static_crop),
                slice(self.static_crop, img_dims[det_x] - self.static_crop)]
            for ddim in [det_x, det_y]:
                self.shape[ddim] = self.shape[ddim] - 2 * self.static_crop

        elif self.auto_crop:
            xs = np.array([0, 0, img_dims[det_x], img_dims[det_x]]).astype(
                np.float32)
            ys = np.array([0, img_dims[det_x], img_dims[det_x], 0]).astype(
                np.float32)
            r = np.sqrt((xs - self.centre[1]) ** 2 + (ys - self.centre[0]) ** 2)
            theta = np.pi + np.arctan2(xs - self.centre[1], ys - self.centre[0])
            theta_p = theta + self.angle / 180. * np.pi
            x_p = np.sort(self.centre[1] - np.sin(theta_p) * r)
            y_p = np.sort(self.centre[0] - np.cos(theta_p) * r)
            x0 = np.ceil(max(x_p[0], x_p[1], 0)).astype(int)
            x1 = np.floor(min(x_p[2], x_p[3], img_dims[det_x])).astype(int)
            y0 = np.ceil(max(y_p[0], y_p[1], 0)).astype(int)
            y1 = np.floor(min(y_p[2], y_p[3], img_dims[det_y])).astype(int)
            self.new_slice = [slice(y0, y1), slice(x0, x1)]
            self.shape[det_x] = x1 - x0
            self.shape[det_y] = y1 - y0

        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=tuple(self.shape))
        out_pData[0].plugin_data_setup('PROJECTION', 'single')
