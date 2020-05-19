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
.. module:: Convert 360-180 sinogram.
   :platform: Unix
   :synopsis: A plugin working in sinogram space to convert 0-360 degree\\
    sinogram to 0-180 sinogram.
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.data.plugin_list import CitationInformation
import numpy as np
import scipy.ndimage as ndi


@register_plugin
class Convert360180Sinogram(Plugin, CpuPlugin):
    """

    Method to convert the 0-360 degree sinogram to 0-180 sinogram.
    :param center: Center of rotation. Default: 0.0
    :param out_datasets: Create a list of the dataset(s) to \
        create. Default: ['in_datasets[0]', 'cor'].

    """

    def __init__(self):
        super(Convert360180Sinogram, self).__init__(
            "Convert360180Sinogram")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()

        self.center = 0.0
        key = "centre_of_rotation"
        if key in in_dataset[0].meta_data.get_dictionary().keys():
            self.center = in_dataset[0].meta_data.get(key)

        old_shape = in_dataset[0].get_shape()
        width_dim = in_dataset[0].get_data_dimension_by_axis_label(
            'detector_x')
        self.height1_dim = in_dataset[0].get_data_dimension_by_axis_label(
            'detector_y')

        height_dim = in_dataset[0].get_data_dimension_by_axis_label(
            'rotation_angle')
        new_shape = list(old_shape)
        new_shape[width_dim] *= 2
        new_shape[height_dim] = np.int16(np.ceil(new_shape[height_dim] / 2.0))

        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=tuple(new_shape))
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')

        slice_dirs = np.array(in_dataset[0].get_slice_dimensions())
        new_shape = (np.prod(np.array(old_shape)[slice_dirs]), 1)
        self.orig_shape = (np.prod(np.array(old_shape)[slice_dirs]), 1)

        out_dataset[1].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      transport='hdf5')
        out_dataset[1].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))

        out_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[1].plugin_data_setup('METADATA', 'single')

    def pre_process(self):
        out_dataset = self.get_out_datasets()[0]
        in_pData = self.get_plugin_in_datasets()
        width_dim = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        height_dim = in_pData[0].get_data_dimension_by_axis_label(
            'rotation_angle')
        sino_shape = list(in_pData[0].get_shape())
        self.width = sino_shape[width_dim]
        self.height = sino_shape[height_dim]
        center_manu = float(self.parameters['center'])
        if center_manu != 0.0:
            self.center = center_manu
        self.mid_width = self.width / 2.0
        if (self.center <= 0) or (self.center > self.width):
            self.center = self.mid_width
        center_int = np.int16(np.floor(self.center))
        self.subpixel_shift = self.center - center_int
        if self.center < self.mid_width:
            self.overlap = 2 * center_int
            self.cor = self.width + center_int
        else:
            self.overlap = 2 * (self.width - center_int)
            self.cor = center_int

        self.new_height = np.int16(np.ceil(self.height / 2.0))
        list_angle = out_dataset.meta_data.get("rotation_angle")
        list_angle = list_angle[0:self.new_height]

        out_dataset.meta_data.set("rotation_angle", list_angle)
        list_wedge = np.linspace(1.0, 0.0, self.overlap)
        self.mat_wedge_left = \
            np.ones((self.new_height, self.width), dtype=np.float32)
        self.mat_wedge_left[:, -self.overlap:] = np.float32(list_wedge)
        self.mat_wedge_right = np.fliplr(self.mat_wedge_left)

    def process_frames(self, data):
        sinogram = np.copy(data[0])
        sinogram = ndi.interpolation.shift(sinogram, (0, -self.subpixel_shift),
                                           prefilter=False, mode='nearest')
        sinogram1 = sinogram[:self.new_height]
        sinogram2 = np.fliplr(sinogram[-self.new_height:])
        sinocombine = np.zeros((self.new_height, 2 * self.width),
                               dtype=np.float32)
        if self.center < self.mid_width:
            num1 = np.mean(np.abs(sinogram1[:, :self.overlap]))
            num2 = np.mean(np.abs(sinogram2[:, -self.overlap:]))
            sinogram2 = sinogram2 * num1 / num2
            sinogram1 = sinogram1 * self.mat_wedge_right
            sinogram2 = sinogram2 * self.mat_wedge_left
            sinocombine[:, 0:self.overlap] = sinogram2[:, 0:1]
            sinocombine[:, self.overlap:self.overlap + self.width] = sinogram2
            sinocombine[:, -self.width:] += sinogram1
        else:
            num1 = np.mean(np.abs(sinogram1[:, -self.overlap:]))
            num2 = np.mean(np.abs(sinogram2[:, :self.overlap]))
            sinogram2 = sinogram2 * num1 / num2
            sinogram1 = sinogram1 * self.mat_wedge_left
            sinogram2 = sinogram2 * self.mat_wedge_right
            sinocombine[:, 0:self.width] = sinogram1
            sinocombine[:, self.width - self.overlap:
                        2 * self.width - self.overlap] += sinogram2
            sinocombine[:, -self.overlap:] = sinogram2[:, -1:]
        return [sinocombine, np.array([self.cor])]

    def nOutput_datasets(self):
        return 2
