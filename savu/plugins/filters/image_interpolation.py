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
.. module:: image_interpolation
   :platform: Unix
   :synopsis: A plugin to interpolate each frame

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy as np
# TODO replace imresize with PIL Image
# from scipy.misc import imresize
from PIL import Image

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin, dawn_compatible


@register_plugin
@dawn_compatible
class ImageInterpolation(BaseFilter, CpuPlugin):
    """
    A plugin to interpolate an image by a factor
    
    :param size: int, float or tuple. Default: 2.0.
    :param interp: nearest lanczos bilinear bicubic cubic. Default:'bicubic'.
    """

    def __init__(self):
        logging.debug("Starting ImageInterpolation")
        super(ImageInterpolation,
              self).__init__("ImageInterpolation")

    def process_frames(self, data):
        data = data[0]
        return self.imresize(data, self.parameters['size'],
                        self.parameters['interp'], mode=None)

    def setup(self):
        # get all in and out datasets required by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # get plugin specific instances of these datasets
        in_pData, out_pData = self.get_plugin_datasets()

        in_pData[0].plugin_data_setup(self.get_plugin_pattern(),
                                      self.get_max_frames())
        inshape = in_dataset[0].get_shape()
        imshape = inshape[-2:]
        restshape = inshape[:-2]
        outshape = self.imresize(np.ones(imshape), self.parameters['size'],
                                 self.parameters['interp'], None).shape
        outshape = restshape + outshape
        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=outshape)

        out_pData[0].plugin_data_setup(self.get_plugin_pattern(),
                                       self.get_max_frames())

    def imresize(self, data, size, interp, mode):
        """
        Provides an imresize implementation, as it is removed from scipy 1.3.0
        Uses PIL.Image, following docs advice from
        https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.misc.imresize.html
        """
        return np.array(Image.fromarray(data, mode).resize(size, interp))

    def get_max_frames(self):
        return 1

    def get_plugin_pattern(self):
        return "PROJECTION"
