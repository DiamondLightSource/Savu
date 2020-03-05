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

    :u*param cropX: Crop in pixels applied to the x-dimensions (on each side).\
    Default: 0.
    :u*param cropY: Crop in pixels applied to the y-dimensions (on each side).\
    Default: 0.
    :u*param mode: Select the mode: (absolute|relative|automatic). \
    Absolute will use the sizeX/Y parameters to determine the final size, \
    relative will crop the images by the amount specified in cropX/Y and \
    automatic will use metadata to determine the cropping size. \
    Default: 'absolute'.
    :u*param sizeX: The x-size of the cropped image in pixels. A setting of -1\
    means the original size will be preserved. Default: -1.
    :u*param sizeY: The y-size of the cropped image in pixels. A setting of -1\
    means the original size will be preserved. Default: -1.
    """

    def __init__(self):
        super(CropProjections, self).__init__("CropProjections")

    def pre_process(self):
        pass

    def process_frames(self, data):
        #in_dataset, out_dataset = self.get_datasets()
        #print(in_dataset[0].meta_data.get("indices2crop"))
        #indices2crop = in_dataset[0].meta_data.get('indices2crop')
        #shapeX = int(indices2crop[1]-indices2crop[0])
        #shapeY = int(indices2crop[3]-indices2crop[2])
        #print(shapeX, shapeY)
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
        img_dims = self.get_in_datasets()[0].get_shape()

        if self.parameters['mode'] == 'absolute':
            sizeX = self.parameters['sizeX']
            sizeY = self.parameters['sizeY']
            if sizeX > 0:
                xslice = slice(self.shape[det_x] / 2 - sizeX / 2,
                self.shape[det_x] / 2 + sizeX / 2 + sizeX % 2)
                self.shape[det_x] = 2 * (sizeX / 2) + sizeX % 2
            else:
                xslice = slice(0, self.shape[det_x])
            if sizeY > 0:
                yslice = slice(self.shape[det_y] / 2 - sizeY / 2,
                self.shape[det_y] / 2 + sizeY / 2 + sizeY % 2)
                self.shape[det_y] = 2 * (sizeY / 2) + sizeY % 2
            else:
                yslice = slice(0, self.shape[det_y])
            self.new_slice = [yslice, xslice]
        elif self.parameters['mode'] == 'relative':
            cropX = self.parameters['cropX']
            cropY = self.parameters['cropY']
            self.new_slice = [slice(cropY, img_dims[det_y] - cropY),
                 slice(cropX, img_dims[det_x] - cropX)]
            self.shape[det_x] -= 2 * cropX
            self.shape[det_y] -= 2 * cropY
        elif self.parameters['mode'] == 'automatic':
            print(in_dataset[0].get_name())
            print(in_dataset[0].meta_data.get_dictionary().keys())         
            for key, value in in_dataset[0].meta_data.get_dictionary().iteritems():
                print (key, value)
            
            #print(in_dataset[0].meta_data.get('indices2crop'))
            # getting indices to crop the data            
            #sample_data[int(indices2crop[2]):int(indices2crop[3]),int(indices2crop[0]):int(indices2crop[1])]
            #indices2crop = in_dataset[0].meta_data.get('indices2crop')
            #shapeX = int(indices2crop[1]-indices2crop[0])
            #shapeY = int(indices2crop[3]-indices2crop[2])
            #self.new_slice = [slice(indices2crop[0], indices2crop[1]),
            #     slice(indices2crop[2], indices2crop[3])]
            #self.new_slice = [slice(indices2crop[2], indices2crop[3]),
            #     slice(indices2crop[0], indices2crop[1])]
            #print(shapeX, shapeY)
            #self.shape[det_x] = shapeX
            #self.shape[det_y] = shapeY
            #print(img_dims[det_x], img_dims[det_y])            
            self.new_slice = (None, None)

        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                      axis_labels=in_dataset[0],
                                      shape=tuple(self.shape))
        out_pData[0].plugin_data_setup('PROJECTION', 'single')  
        