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
.. module:: ImageInterpolation
   :platform: Unix
   :synopsis: A plugin to interpolate each frame

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy as np
from scipy.misc import imresize

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin, dawn_compatible

from skimage.util.shape import view_as_windows as viewW

from scipy.ndimage.interpolation import map_coordinates


@register_plugin
@dawn_compatible
class SpiralRemap(BaseFilter, CpuPlugin):
    """
    A plugin to unwrap a spirl scan
    :param y_per_theta: how much y changes per degree of rotation. Default: 1.0.
    :param interp: nearest lanczos bilinear bicubic cubic. Default:'bicubic'.
    """

    def __init__(self):
        logging.debug("Starting SpiralRemap")
        super(SpiralRemap,
              self).__init__("SpiralRemap")


    def process_frames(self, data):
        # get the angles out of the metadata
        in_meta_data = self.get_in_meta_data()[0]
        angles = in_meta_data.get('rotation_angle')

        offsets = angles*self.parameters['y_per_theta']
        offsets = offsets-offsets.min()
        max_height = int(np.ceil(offsets.max()))

        #TODO fix this hardcoded value for number of rotation angles
        full_rotation = 3600

        pitch = 360*self.parameters['y_per_theta']
        pitch_step = pitch/full_rotation

        # build the remapping mesh
        mapy, mapx, mapz = np.meshgrid(np.arange(0, max_height),
                                       range(data[0].shape[0]),
                                       range(data[0].shape[2]))

        mapy = mapy - offsets.reshape(offsets.shape[0],1,1)

        mapx[mapy>=(data[0].shape[1])] = -1
        mapx[mapy<0] = -1

        sections = np.split(mapx, np.arange(0, mapx.shape[0],full_rotation)[1::])

        mapx = np.max(np.stack(sections[:-1], axis=3), axis=3)

        mapy[mapy>=(data[0].shape[1])] = -1
        mapy[mapy<0] = -1

        sections = np.split(mapy, np.arange(0, mapy.shape[0],full_rotation)[1::])

        mapy = np.max(np.stack(sections[:-1], axis=3), axis=3)

        mapz = mapz[:full_rotation, :, :]


        # Apply the data, and then 
        remapped_data = map_coordinates(data[0], [mapx, mapy-1, mapz], cval=0)

        return remapped_data


    def setup(self):
        # get all in and out datasets required by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # get plugin specific instances of these datasets
        in_pData, out_pData = self.get_plugin_datasets()

        in_pData[0].plugin_data_setup(self.get_plugin_pattern(), self.get_max_frames())
        inshape = in_dataset[0].get_shape()
        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=inshape)

        out_pData[0].plugin_data_setup(self.get_plugin_pattern(), self.get_max_frames())

    def get_max_frames(self):
        return 5

    def get_plugin_pattern(self):
        return "TANGENTOGRAM"
