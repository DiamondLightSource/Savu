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
.. module:: tiff_saver
   :platform: Unix
   :synopsis: A class to save output in tiff format

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import tifffile as tf

from savu.plugins.savers.base_image_saver import BaseImageSaver
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class TiffSaver(BaseImageSaver, CpuPlugin):
    def __init__(self, name='TiffSaver'):
        super(TiffSaver, self).__init__(name)

    def process_frames(self, data):
        frame = self.get_global_frame_index()[self.count]
        filename = '%s%05i.tiff' % (self.filename, frame)
        tf.imsave(filename, data[0])
        self.count += 1
