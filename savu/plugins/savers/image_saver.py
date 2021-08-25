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
.. module:: image_saver
   :platform: Unix
   :synopsis: A class to save output as images

.. moduleauthor:: Dan Nixon, Nghia Vo <scientificsoftware@diamond.ac.uk>

"""

import logging
import skimage.exposure
import skimage.io
import numpy as np
from PIL import Image

from savu.plugins.savers.base_image_saver import BaseImageSaver
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
import savu.core.utils as cu


@register_plugin
class ImageSaver(BaseImageSaver, CpuPlugin):
    def __init__(self, name='ImageSaver'):
        super(ImageSaver, self).__init__(name)

    def setup(self):
        data_pattern = self.parameters['pattern']
        in_pData, _ = self.get_plugin_datasets()
        try:
            in_pData[0].plugin_data_setup(data_pattern, 'single')
        except:
            msg = "\n***************************************************"\
            "**********\n"\
            "Can't find the data pattern: {}.\nThe pattern parameter of " \
            "this plugin must be relevant to its \nprevious plugin" \
            "\n*************************************************************"\
            "\n".format(data_pattern)
            logging.warning(msg)
            cu.user_message(msg)
            raise ValueError(msg)

    def pre_process(self):
        super(ImageSaver, self).pre_process()
        self.pData = self.get_plugin_in_datasets()[0]
        self.file_format = self.parameters['format']
        num_bit = self.parameters['num_bit']
        if not (num_bit == 8 or num_bit == 16 or num_bit == 32):
            self.num_bit = 32
            msg = "\n***********************************************\n"\
                "This option %s is not available. Reset to 32 \n"\
                % str(num_bit)
            cu.user_message(msg)
        else:
            self.num_bit = num_bit
        self._data_range = self._get_min_and_max()

    def process_frames(self, data):
        frame = self.pData.get_current_frame_idx()[0]
        filename = '%s%05i.%s' % (self.filename, frame, self.file_format)
        frame = np.nan_to_num(data[0])
        if (self.file_format == "tiff") or (self.file_format == "tif"):
            global_min = self.parameters['min']
            global_max = self.parameters['max']
            if self.num_bit == 32:
                rescaled_image = frame
            else:
                if global_min is None:
                    if self.the_min is not None:
                        global_min = self.the_min
                    else:
                        global_min = np.min(frame)
                if global_max is None:
                    if self.the_max is not None:
                        global_max = self.the_max
                    else:
                        global_max = np.max(frame)
                rescaled_image = np.clip(frame, global_min, global_max)
                rescaled_image = (rescaled_image - global_min) \
                    / (global_max - global_min)
                if self.num_bit == 16:
                    rescaled_image = np.clip(
                        np.uint16(rescaled_image * 65535), 0, 65535)
                else:
                    rescaled_image = np.clip(
                        np.uint8(rescaled_image * 255), 0, 255)
            img = Image.fromarray(rescaled_image)
            img.save(filename)
        else:
            # Rescale image to (0.0, 1.0) range
            rescaled_image = skimage.exposure.rescale_intensity(
                frame, in_range=self._data_range, out_range=(0.0, 1.0))
            # Save image
            skimage.io.imsave(
                filename, rescaled_image, quality=self.parameters['jpeg_quality'])

    def _get_min_and_max(self):
        data = self.get_in_datasets()[0]
        pattern = self.parameters['pattern']
        try:
            self.the_min = np.min(
                data.meta_data.get(['stats', 'min', pattern]))
            self.the_max = np.max(
                data.meta_data.get(['stats', 'max', pattern]))
            self._data_range = (self.the_min, self.the_max)
        except KeyError:
            self._data_range = 'image'
            if (self.file_format == "tiff") or (self.file_format == "tif"):
                self.the_min = None
                self.the_max = None
                msg = "\n***********************************************\n"\
                    "!!!Warning!!!-> No global maximum and global minimum found\n"\
                    "in the metadata. Please run the MaxAndMin plugin before\n" \
                    "ImageSaver or input manually. Otherwise, local minimum\n" \
                    "and local maximum will be used for rescaling. This may\n"\
                    "result the fluctuation of brightness between slices.\n"\
                    "***********************************************\n"
                if (self.num_bit == 8) or (self.num_bit == 16):
                    cu.user_message(msg)
        return self._data_range

    def executive_summary(self):
        if (self._data_range == 'image') and (self.num_bit != 32):
            return ["To rescale and normalise the data between global max and "
                    "min values, please run MaxAndMin plugin before "
                    "ImageSaver."]
        return ["Nothing to Report"]
