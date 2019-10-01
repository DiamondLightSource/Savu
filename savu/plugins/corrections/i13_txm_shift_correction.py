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
.. module:: i13_txm_shift_correction
   :platform: Unix
   :synopsis: A plugin to apply a shift correction to individual projections
.. moduleauthor:: Malte Storm <malte.storm@diamond.ac.uk>
"""


from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
import scipy.ndimage.interpolation as ip

@register_plugin
class I13TxmShiftCorrection(BaseFilter, CpuPlugin):
    """
    A plugin to apply the shift correction to a I13-2 TXM dataset.
    :u*param autoCrop: If True, the amount of cropping is automatically \
    determined by the image shift values. Default: True.
    :u*param crop_x: If not using autoCrop, determines the amount of cropping. \
    Default: 0
    :u*param crop_y: If not using autoCrop, determines the amount of cropping. \
    Default: 0
    """

    def __init__(self):
        super(I13TxmShiftCorrection, self).__init__("I13TxmShiftCorrection")

    def pre_process(self):
        pass
            
    def process_frames(self, data):
        frame = self.get_global_frame_index()[self.count]
        self.m[1, 2] = self.image_shift[frame, 1]
        self.m[0, 2] = self.image_shift[frame, 0]
        self.count += 1
        return ip.shift(data[0], (self.m[1, 2], self.m[0, 2]), \
            mode='nearest', order=1)[self.slices]
        
    def post_process(self):
        pass

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        
        det_y = in_dataset[0].get_data_dimension_by_axis_label('detector_y')
        det_x = in_dataset[0].get_data_dimension_by_axis_label('detector_x')
        shape = list(in_dataset[0].get_shape())
        self.count = 0
        
        in_pData[0].plugin_data_setup('PROJECTION', 'single')
        
        self.image_shift = in_dataset[0].meta_data.get('image_shift')
        self.m = np.asarray([[1., 0., 0], [0., 1., 0], [0., 0., 1.]])
        if self.parameters['autoCrop']:
            xmax = np.amax(np.ceil(abs(self.image_shift[:,0]))).astype(int)
            ymax = np.amax(np.ceil(abs(self.image_shift[:,1]))).astype(int)
        else:
            xmax = self.parameters['crop_x']
            ymax = self.parameters['crop_y']
        
        self.slices = [slice(ymax, shape[det_y] - ymax), 
                       slice(xmax, shape[det_x] - xmax)]
        
        shape[det_x] = shape[det_x] - 2 * xmax
        shape[det_y] = shape[det_y] - 2 * ymax

        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=tuple(shape))
        out_pData[0].plugin_data_setup('PROJECTION', 'single')
        
         

