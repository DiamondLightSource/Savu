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
.. module:: projection_shift
   :platform: Unix
   :synopsis: Calculate horizontal and vertical shifts in the projection\
       images over time, using template matching.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import numpy as np
from skimage.feature import match_template, match_descriptors, ORB
from scipy.linalg import lstsq
from skimage.transform import AffineTransform
from skimage.measure import ransac

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class ProjectionShift(BaseFilter, CpuPlugin):
    """
    """

    def __init__(self):
        logging.debug("initialising Sinogram Alignment")
        super(ProjectionShift, self).__init__("ProjectionShift")
        self.template = None
        self.threshold = 0

    def pre_process(self):
        if self.parameters['method'] == 'template_matching':
            self.template_params = []
            for p in self.parameters['template']:
                start, end = p.split(':')
                self.template_params.append(slice(int(start), int(end)))
            self._calculate_shift = self._template_matching_shift
        elif self.parameters['method'] == 'orb_ransac':
            self._calculate_shift = self._orb_ransac_shift

        if self.parameters['threshold']:
            self.threshold = self.parameters['threshold']

        self.sl = [slice(None)]*3
        self.sl2 = [slice(None)]*3
        self.slice_dir = self.get_plugin_in_datasets()[0].get_slice_dimension()
        self.A = self._calculate_frame_matrix()

    def _calculate_frame_matrix(self):
        n_unknowns = self.get_max_frames() + 2  # 2 padded frames
        frame_list = self._calculate_frame_list(np.arange(n_unknowns))
        n_equations = len(frame_list)
        A = np.zeros((n_equations, n_unknowns))
        for i in range(len(frame_list)):
            for f in frame_list[i][1:]:
                A[i, f] = 1
        return A

    def process_frames(self, data):
        data, nFrames, output, shift_array = self._initial_setup(data)
        return self._sub_pixel_shift_adjustment(data)

    def _initial_setup(self, data):
        data = data[0]
        shape = list(data.shape)
        nFrames = data.shape[self.slice_dir]-2
        shape[self.slice_dir] += -2
        output = np.zeros(tuple(shape))
        shift_array = np.zeros((nFrames, 2))
        return data, nFrames, output, shift_array

    def _get_shift(self, data, frame1, frame2):
        self.sl[self.slice_dir] = frame1
        self.sl2[self.slice_dir] = frame2

        d1 = data[self.sl]
        d2 = data[self.sl2]
        if self.template:
            self.template = data[self.sl][self.template_params]

        if self.threshold:
            d1[d1 > self.threshold[0]] = self.threshold[1]
            d2[d2 > self.threshold[0]] = self.threshold[1]
            if self.template:
                self.template[self.template > self.threshold[0]] = \
                    self.threshold[1]
        return self._calculate_shift(d1, d2, self.template)

    def _orb_ransac_shift(self, im1, im2, template):
        descriptor_extractor = ORB() #n_keypoints=self.parameters['n_keypoints'])
        key1, des1 = self._find_key_points(descriptor_extractor, im1)
        key2, des2 = self._find_key_points(descriptor_extractor, im2)
        matches = match_descriptors(des1, des2, cross_check=True)

        # estimate affine transform model using all coordinates
        src = key1[matches[:, 0]]
        dst = key2[matches[:, 1]]

        # robustly estimate affine transform model with RANSAC
        model_robust, inliers = ransac((src, dst), AffineTransform,
                                       min_samples=3, residual_threshold=1,
                                       max_trials=100)
#        diff = []
#        for p1, p2 in zip(src[inliers], dst[inliers]):
#            diff.append(p2-p1)
#        return np.mean(diff, axis=0)

        return model_robust.translation

    def _find_key_points(self, desc_extractor, image):
        desc_extractor.detect_and_extract(image)
        keypoints = desc_extractor.keypoints
        descriptors = desc_extractor.descriptors
        return keypoints, descriptors

    def _template_matching_shift(self, im1, im2, template):
        index = []
        for im in [im1, im2]:
            match = match_template(im, template)
            index.append(np.unravel_index(np.argmax(match), match.shape))
        index = np.array(index)
        shift = index[1] - index[0]
        return shift

    def _sub_pixel_shift_adjustment(self, data):
        frame_list = \
            self._calculate_frame_list(np.arange(data.shape[self.slice_dir]))

        new_shift = []
        for f in frame_list:
            new_shift.append(
                self._get_shift(data, f[0], f[-1]).astype(np.float64))

        return self._calculate_new_shift_array(np.array(new_shift))

    def _calculate_frame_list(self, frames):
        sixes = list(zip(*(frames[i:] for i in range(6))))
        fives = list(zip(*(frames[i:] for i in range(5))))
        fours = list(zip(*(frames[i:] for i in range(4))))
        threes = list(zip(*(frames[i:] for i in range(3))))
        return sixes + fives + fours + threes

    def _calculate_new_shift_array(self, shift):
        new_shift = []
        for i in range(2):
            new_shift.append(lstsq(self.A, shift[:, i])[0])
        return np.transpose(np.array(new_shift))[1:-1]

    def post_process(self):
        out_data = self.get_out_datasets()[0]
        self.get_in_datasets()[0].meta_data.set(
            'proj_align_shift_local', out_data.data[:, :])
        self.get_in_datasets()[0].meta_data.set(
            'proj_align_shift', np.cumsum(out_data.data[:, :], axis=0))

    def get_max_frames(self):
        # Do not change this number as 8 is currently a requirement.
        return 8

    def nOutput_datasets(self):
        return 1

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames(),
                                      fixed=True)

        new_shape = (in_dataset[0].get_shape()[
            in_dataset[0].get_slice_directions()[0]], 2)

        out_dataset[0].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True)
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames(),
                                       fixed=True)

    def set_filter_padding(self, in_data, out_data):
        pad_dim = in_data[0].get_slice_directions()[0]
        in_data[0].padding = {'pad_directions': [str(pad_dim) + '.1']}
        #in_data[0].padding = {'pad_directions': [str(pad_dim) + '.before.1']}
