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

.. moduleauthor:: Dan Nixon <daniel.nixon@stfc.ac.uk>

"""

import skimage.exposure
import skimage.io
import numpy as np

from savu.plugins.savers.base_image_saver import BaseImageSaver
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class ImageSaver(BaseImageSaver, CpuPlugin):
    """
    A class to save tomography data to image files
    :param pattern: How to slice the data. Default: 'VOLUME_XZ'.
    :param format: Image format. Default: 'jpeg'.
    :param jpeg_quality: JPEG encoding quality (1 is worst, 100 is best). Default: 75.
    :param prefix: Override the default output jpg file prefix. Default: None.

    :config_warn: Do not use this plugin if the raw data is greater than \
    100 GB.
    """

    def __init__(self, name='ImageSaver'):
        super(ImageSaver, self).__init__(name)

    def pre_process(self):
        super(ImageSaver, self).pre_process()

        # Get max and min pixel intensities across entire dataset
        # TODO: Replace this with a read time calculation of min and max pixel
        # intensities (see commit message for more information)
        data = self.get_in_datasets()[0].data
        self._data_range = (np.min(data), np.max(data))

    def process_frames(self, data):
        frame = self.get_global_frame_index()[0][self.count]
        filename = '%s%05i.%s' % (self.filename, frame, self.parameters['format'])

        # Rescale image to (0.0, 1.0) range
        resampled_image = skimage.exposure.rescale_intensity(
                data[0], in_range=self._data_range, out_range=(0.0, 1.0))

        # Save image
        skimage.io.imsave(
                filename, resampled_image, quality=self.parameters['jpeg_quality'])

        self.count += 1
