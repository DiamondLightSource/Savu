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


    def strided_indexing_roll(self, a, r):
        # Concatenate with sliced to cover all rolls
        p = np.full((a.shape[0],a.shape[1]-1),np.nan)
        a_ext = np.concatenate((p,a,p),axis=1)
        # Get sliding windows; use advanced-indexing to select appropriate ones
        n = a.shape[1]
        return viewW(a_ext,(1,n))[np.arange(len(r)), -r + (n-1),0]



    def _apply_offset(self, data, angles):
        offsets = angles*self.parameters['y_per_theta']
        max_height = int(data.shape[1]+np.ceil(offsets.max()))
        remap = np.zeros((data.shape[0], max_height, data.shape[2]))
        
        off = ((offsets-offsets.min())*10).astype(np.int16)
        slice = data[:,:,70]
        
        rollshape = list(slice.shape)
        rollshape[1] = off.max()
        
        p = np.full(tuple(rollshape), np.nan)
        
        a_ext = np.concatenate((slice, p), axis=1)
        
        for i in range(off.shape[0]):
            a_ext[i, :] = np.roll(a_ext[i,:], off[i])
        
        
        #TODO : Actually remap 
        return a_ext


    def _restack_360(self, data, angles):
        #TODO actually implement
        pass

    def process_frames(self, data):
        # get the angles out of the metadata
        in_meta_data = self.get_in_meta_data()[0]
        angles = in_meta_data.get('rotation_angle')
        offset = self._apply_offset(data[0], angles)
        remap = self._restack_360(offset, angles)
        return remap

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
        return 'multiple'

    def get_plugin_pattern(self):
        return "TANGENTOGRAM"
