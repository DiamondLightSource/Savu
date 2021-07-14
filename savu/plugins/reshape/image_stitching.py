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
.. module:: image_stitching
   :platform: Unix
   :synopsis: A plugin for stitching two tomo-datasets.
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
import copy
import numpy as np
import scipy.ndimage as ndi
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class ImageStitching(Plugin, CpuPlugin):
    def __init__(self):
        super(ImageStitching, self).__init__('ImageStitching')

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        self.space = self.parameters['pattern']

        if self.space == 'SINOGRAM':
            in_pData[0].plugin_data_setup('SINOGRAM_STACK', 2,
                                          fixed_length=False)
        else:
            in_pData[0].plugin_data_setup('PROJECTION_STACK', 2,
                                          fixed_length=False)
        rm_dim = in_dataset[0].get_slice_dimensions()[0]
        patterns = ['SINOGRAM.' + str(rm_dim), 'PROJECTION.' + str(rm_dim)]

        self.c_top, self.c_bot, self.c_left, self.c_right = self.parameters[
            'crop']
        self.overlap = int(self.parameters['overlap'])
        self.row_offset = int(self.parameters['row_offset'])
        self.norm = self.parameters['norm']
        self.flat_use = self.parameters['flat_use']

        axis_labels = copy.copy(in_dataset[0].get_axis_labels())
        del axis_labels[rm_dim]
        width_dim = in_dataset[0].get_data_dimension_by_axis_label(
            'detector_x')
        height_dim = in_dataset[0].get_data_dimension_by_axis_label(
            'detector_y')
        shape = list(in_dataset[0].get_shape())

        shape[width_dim] = 2 * shape[width_dim] - \
                           self.overlap - self.c_left - self.c_right
        if self.space == 'PROJECTION':
            shape[height_dim] = shape[height_dim] - self.c_top - self.c_bot
        del shape[rm_dim]
        out_dataset[0].create_dataset(
            patterns={in_dataset[0]: patterns},
            axis_labels=axis_labels,
            shape=tuple(shape))
        if self.space == 'SINOGRAM':
            out_pData[0].plugin_data_setup('SINOGRAM', 'single',
                                           fixed_length=False)
        else:
            out_pData[0].plugin_data_setup('PROJECTION', 'single',
                                           fixed_length=False)

    def make_weight_matrix(self, height1, width1, height2, width2, overlap,
                           side):
        """
        Generate a linear-ramp weighting matrix for image stitching.

        Parameters
        ----------
        height1, width1 : int
            Size of the 1st image.
        height2, width2 : int
            Size of the 2nd image.
        overlap : int
            Width of the overlap area between two images.
        side : {0, 1}
            Only two options: 0 or 1. It is used to indicate the overlap side
            respects to image 1. "0" corresponds to the left side. "1"
            corresponds to the right side.
        """
        overlap = int(np.floor(overlap))
        wei_mat1 = np.ones((height1, width1), dtype=np.float32)
        wei_mat2 = np.ones((height2, width2), dtype=np.float32)
        if side == 1:
            list_down = np.linspace(1.0, 0.0, overlap)
            list_up = 1.0 - list_down
            wei_mat1[:, -overlap:] = np.float32(list_down)
            wei_mat2[:, :overlap] = np.float32(list_up)
        else:
            list_down = np.linspace(1.0, 0.0, overlap)
            list_up = 1.0 - list_down
            wei_mat2[:, -overlap:] = np.float32(list_down)
            wei_mat1[:, :overlap] = np.float32(list_up)
        return wei_mat1, wei_mat2

    def stitch_image(self, mat1, mat2, overlap, side, wei_mat1, wei_mat2, norm):
        """
        Stitch projection images or sinogram images using a linear ramp.

        Parameters
        ----------
        mat1 : array_like
            2D array. Projection image or sinogram image.
        mat2 :  array_like
            2D array. Projection image or sinogram image.
        overlap : float
            Width of the overlap area between two images.
        side : {0, 1}
            Only two options: 0 or 1. It is used to indicate the overlap side
            respects to image 1. "0" corresponds to the left side. "1"
            corresponds to the right side.
        wei_mat1 : array_like
            Weighting matrix used for image 1.
        wei_mat2 : array_like
            Weighting matrix used for image 2.
        norm : bool, optional
            Enable/disable normalization before stitching.

        Returns
        -------
        array_like
            Stitched image.
        """
        (nrow1, ncol1) = mat1.shape
        (nrow2, ncol2) = mat2.shape
        overlap_int = int(np.floor(overlap))
        sub_pixel = overlap - overlap_int
        if sub_pixel > 0.0:
            if side == 1:
                mat1 = ndi.shift(mat1, (0, sub_pixel), mode='nearest')
                mat2 = ndi.shift(mat2, (0, -sub_pixel), mode='nearest')
            else:
                mat1 = ndi.shift(mat1, (0, -sub_pixel), mode='nearest')
                mat2 = ndi.shift(mat2, (0, sub_pixel), mode='nearest')
        if nrow1 != nrow2:
            raise ValueError("Two images are not at the same height!!!")
        total_width0 = ncol1 + ncol2 - overlap_int
        mat_comb = np.zeros((nrow1, total_width0), dtype=np.float32)
        if side == 1:
            if norm is True:
                factor1 = np.mean(mat1[:, -overlap_int:])
                factor2 = np.mean(mat2[:, :overlap_int])
                mat2 = mat2 * factor1 / factor2
            mat_comb[:, 0:ncol1] = mat1 * wei_mat1
            mat_comb[:, (ncol1 - overlap_int):total_width0] += mat2 * wei_mat2
        else:
            if norm is True:
                factor2 = np.mean(mat2[:, -overlap_int:])
                factor1 = np.mean(mat1[:, :overlap_int])
                mat2 = mat2 * factor1 / factor2
            mat_comb[:, 0:ncol2] = mat2 * wei_mat2
            mat_comb[:, (ncol2 - overlap_int):total_width0] += mat1 * wei_mat1
        return mat_comb

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        self.data_size = inData.get_shape()
        shape = len(self.get_plugin_in_datasets()[0].get_shape())
        (self.depth0, self.height0, self.width0, _) = inData.get_shape()
        self.sl1 = [slice(None)] * (shape - 1) + [0]
        self.sl2 = [slice(None)] * (shape - 1) + [1]
        if self.flat_use is True:
            dark = inData.data.dark_mean()
            flat = inData.data.flat_mean()
            (h_df, w_df) = dark.shape
            dark1 = dark[:h_df // 2]
            flat1 = flat[:h_df // 2]
            dark2 = dark[-h_df // 2:]
            flat2 = flat[-h_df // 2:]
            if self.space == 'SINOGRAM':
                self.dark1 = 1.0 * dark1[:, self.c_left:]
                self.flat1 = 1.0 * flat1[:, self.c_left:]
                self.dark2 = 1.0 * dark2[:, :w_df - self.c_right]
                self.flat2 = 1.0 * flat2[:, :w_df - self.c_right]
            else:
                self.dark1 = 1.0 * \
                             dark1[self.c_top: h_df // 2 - self.c_bot,
                             self.c_left:]
                self.flat1 = 1.0 * \
                             flat1[self.c_top: h_df // 2 - self.c_bot,
                             self.c_left:]
                dark2 = np.roll(dark2, self.row_offset, axis=0)
                flat2 = np.roll(flat2, self.row_offset, axis=0)
                self.dark2 = 1.0 * dark2[self.c_top: h_df // 2 -
                                                     self.c_bot,
                                   :w_df - self.c_right]
                self.flat2 = 1.0 * flat2[self.c_top: h_df // 2 -
                                                     self.c_bot,
                                   :w_df - self.c_right]
            self.flatdark1 = self.flat1 - self.dark1
            self.flatdark2 = self.flat2 - self.dark2
            nmean = np.mean(np.abs(self.flatdark1))
            self.flatdark1[self.flatdark1 == 0.0] = nmean
            nmean = np.mean(np.abs(self.flatdark2))
            self.flatdark2[self.flatdark2 == 0.0] = nmean
        if self.space == 'SINOGRAM':
            (_, w_df1) = self.dark1.shape
            (_, w_df2) = self.dark2.shape
            (self.wei1, self.wei2) = self.make_weight_matrix(
                self.depth0, w_df1, self.depth0, w_df2, self.overlap, 1)
        else:
            (h_df1, w_df1) = self.dark1.shape
            (h_df2, w_df2) = self.dark2.shape
            (self.wei1, self.wei2) = self.make_weight_matrix(
                h_df1, w_df1, h_df2, w_df2, self.overlap, 1)

        outData = self.get_out_datasets()[0]
        angles = inData.meta_data.get("rotation_angle")[:, 0]
        outData.meta_data.set("rotation_angle", angles)

    def process_frames(self, data):
        mat1 = data[0][tuple(self.sl1)]
        mat2 = data[0][tuple(self.sl2)]
        if self.space == 'SINOGRAM':
            mat1 = np.float32(mat1[:, self.c_left:])
            mat2 = np.float32(mat2[:, :self.width0 - self.c_right])
            if self.flat_use is True:
                count = self.get_process_frames_counter()
                current_idx = self.get_global_frame_index()[count]
                mat1 = (mat1 - self.dark1[current_idx]) \
                       / self.flatdark1[current_idx]
                mat2 = (mat2 - self.dark2[current_idx]) \
                       / self.flatdark2[current_idx]
        else:
            mat1 = np.float32(
                mat1[self.c_top:self.height0 - self.c_bot, self.c_left:])
            mat2 = np.roll(mat2, self.row_offset, axis=0)
            mat2 = np.float32(mat2[self.c_top:self.height0 -
                                              self.c_bot,
                              :self.width0 - self.c_right])
            if self.flat_use is True:
                mat1 = (mat1 - self.dark1) / self.flatdark1
                mat2 = (mat2 - self.dark2) / self.flatdark2
        mat = self.stitch_image(mat1, mat2, self.overlap,
                                1, self.wei1, self.wei2, self.norm)
        return mat
