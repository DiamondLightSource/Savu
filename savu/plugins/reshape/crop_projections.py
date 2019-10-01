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
.. module:: crop_projections
   :platform: Unix
   :synopsis: A plugin to crop projections images without the need to specify 
   preview dimensions.
.. moduleauthor:: Malte Storm<malte.storm@diamond.ac.uk>
"""


from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

@register_plugin
class CropProjections(Plugin, CpuPlugin):
    """
    A plugin to apply apply a crop to projection images without the need to \
    specify preview dimensions. The crop will always be applied symmetrically \
    to the original image.
     
    :u*param xcrop: Crop in pixels applied to the x-dimensions (on each side).\
    Default: 0.
    :u*param ycrop: Crop in pixels applied to the y-dimensions (on each side).\
    Default: 0.
    :u*param useAbsoluteSizes: If True, absolute xsize and ysize parameters \
    will be used to determine the new image size. If False, the image will be \
    cropped by xcrop and ycrop parameters. Default: True.
    :u*param xsize: The x-size of the cropped image in pixels. A setting of -1\
    means the original size will be preserved. Default: -1.
    :u*param ysize: The y-size of the cropped image in pixels. A setting of -1\
    means the original size will be preserved. Default: -1.
    """

    def __init__(self):
        super(CropProjections, self).__init__("CropProjections")

    def pre_process(self):
        pass
            
    def process_frames(self, data):
        return data[0][self.new_slice]

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
        self.xcrop = self.parameters['xcrop']
        self.ycrop = self.parameters['ycrop']
        self.xsize = self.parameters['xsize']
        self.ysize = self.parameters['ysize']
        self.useAbsoluteSizes = self.parameters['useAbsoluteSizes']

        self.shape = list(in_dataset[0].get_shape())
        self.core_dims = in_pData[0].get_core_dimensions()
        img_dims = self.get_in_datasets()[0].get_shape()

        if self.useAbsoluteSizes:
            if self.xsize > 0:
                xslice = slice(self.shape[det_x] / 2 - self.xsize / 2, \
                self.shape[det_x] / 2 + self.xsize / 2 + self.xsize % 2)
                self.shape[det_x] = 2 * (self.xsize / 2) + self.xsize % 2
            else:
                xslice = slice(0, self.shape[det_x])
            if self.ysize > 0:
                yslice = slice(self.shape[det_y] / 2 - self.ysize / 2, \
                self.shape[det_y] / 2 + self.ysize / 2 + self.ysize % 2)
                self.shape[det_y] = 2 * (self.ysize / 2) + self.ysize % 2
            else:
                yslice = slice(0, self.shape[det_y])
            self.new_slice = [yslice, xslice]
        elif not self.useAbsoluteSizes:
            self.new_slice = \
                [slice(self.ycrop, img_dims[det_y] - self.ycrop), \
                 slice(self.xcrop, img_dims[det_x] - self.xcrop)]
            self.shape[det_x] -= 2 * self.xcrop
            self.shape[det_y] -= 2 * self.ycrop
        
        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=tuple(self.shape))
        out_pData[0].plugin_data_setup('PROJECTION', 'single')

