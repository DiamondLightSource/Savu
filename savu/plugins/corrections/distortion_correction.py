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
.. module:: distortion_correction
   :platform: Unix
   :synopsis: A plugin to apply a distortion correction

.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""

import os
import logging
import numpy as np
from scipy.ndimage import map_coordinates
from scipy import interpolate

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
import savu.core.utils as cu


@register_plugin
class DistortionCorrection(BaseFilter, CpuPlugin):

    def __init__(self):
        super(DistortionCorrection, self).__init__("DistortionCorrection")

    def load_metadata_txt(self, file_path):
        """
        Load distortion coefficients from a text file.
        Order of the infor in the text file:
        xcenter
        ycenter
        factor_0
        factor_1
        factor_2
        ...

        Parameters
        ----------
        file_path : str
            Path to the file

        Returns
        -------
        tuple of float and list of floats
            Tuple of (xcenter, ycenter, list_fact).
        """
        with open(file_path, 'r') as f:
            x = f.read().splitlines()
            list_data = []
            for i in x:
                list_data.append(float(i.split()[-1]))
        xcenter = list_data[0]
        ycenter = list_data[1]
        list_fact = list_data[2:]
        return xcenter, ycenter, list_fact

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', 'single')
        self.shape = list(in_dataset[0].get_shape())
        self.core_dims = in_pData[0].meta_data.get('core_dims')
        self.crop = self.parameters['crop_edges']
        for ddir in self.core_dims:
            self.shape[ddir] = self.shape[ddir] - 2 * self.crop
        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=tuple(self.shape))
        out_pData[0].plugin_data_setup('PROJECTION', 'single')

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        data = self.get_in_datasets()[0]
        name = data.get_name()
        shift = self.exp.meta_data.get(name + '_preview_starts')
        step = self.exp.meta_data.get(name + '_preview_steps')
        x_dim = data.get_data_dimension_by_axis_label('detector_x')
        y_dim = data.get_data_dimension_by_axis_label('detector_y')
        step_check = \
            True if max([step[i] for i in [x_dim, y_dim]]) > 1 else False
        if step_check:
            self.msg = "\n***********************************************\n" \
                       "!!! ERROR !!! -> Plugin doesn't work with the step in" \
                       " the preview larger than 1 \n" \
                       "***********************************************\n"
            logging.warning(self.msg)
            cu.user_message(self.msg)
            raise ValueError(self.msg)

        x_offset = shift[x_dim]
        y_offset = shift[y_dim]
        file_path = self.parameters["file_path"]
        self.msg = ""
        x_center = 0.0
        y_center = 0.0
        if file_path is None:
            x_center = np.asarray(self.parameters['center_from_left'],
                                  dtype=np.float32) - x_offset
            y_center = np.asarray(self.parameters['center_from_top'],
                                  dtype=np.float32) - y_offset
            list_fact = np.float32(tuple(self.parameters['polynomial_coeffs']))
        else:
            if not (os.path.isfile(file_path)):
                self.msg = "!!! No such file: %s !!!" \
                           " Please check the file path" % str(file_path)
                cu.user_message(self.msg)
                raise ValueError(self.msg)
            try:
                (x_center, y_center, list_fact) = self.load_metadata_txt(
                    file_path)
                x_center = x_center - x_offset
                y_center = y_center - y_offset
            except IOError:
                self.msg = "\n*****************************************\n" \
                           "!!! ERROR !!! -> Can't open this file: %s \n" \
                           "*****************************************\n\
                           " % str(file_path)
                logging.warning(self.msg)
                cu.user_message(self.msg)
                raise ValueError(self.msg)

        data_shape = data.get_shape()
        self.height, self.width = data_shape[y_dim], data_shape[x_dim]
        xu_list = np.arange(self.width) - x_center
        yu_list = np.arange(self.height) - y_center
        xu_mat, yu_mat = np.meshgrid(xu_list, yu_list)
        ru_mat = np.sqrt(xu_mat ** 2 + yu_mat ** 2)
        fact_mat = np.sum(
            np.asarray([factor * ru_mat ** i for i,
                                                 factor in
                        enumerate(list_fact)]), axis=0)
        xd_mat = np.float32(np.clip(
            x_center + fact_mat * xu_mat, 0, self.width - 1))
        yd_mat = np.float32(np.clip(
            y_center + fact_mat * yu_mat, 0, self.height - 1))

        diff_y = np.max(yd_mat) - np.min(yd_mat)
        if (diff_y < 1):
            self.msg = "\n*****************************************\n\n" \
                       "!!! ERROR !!! -> You need to increase the preview" \
                       " size for this plugin to work \n\n" \
                       "*****************************************\n"
            logging.warning(self.msg)
            cu.user_message(self.msg)

            raise ValueError(self.msg)
        self.indices = np.reshape(yd_mat, (-1, 1)), \
                       np.reshape(xd_mat, (-1, 1))

    def process_frames(self, data):
        mat_corrected = np.reshape(map_coordinates(
            data[0], self.indices, order=1, mode='reflect'),
            (self.height, self.width))
        return mat_corrected[self.crop:self.height - self.crop,
               self.crop:self.width - self.crop]

    def executive_summary(self):
        if self.msg != "":
            cu.user_message(self.msg)
            raise ValueError(self.msg)
        else:
            return ["Nothing to Report"]
