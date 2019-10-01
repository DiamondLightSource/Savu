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
.. module:: tiff_saver_16bit
   :platform: Unix
   :synopsis: A class to save output in tiff format
.. moduleauthor:: Malte Storm <malte.storm@diamond.ac.uk>
"""

from mpi4py import MPI
import tifffile as tf
import os
import numpy as np

from savu.plugins.savers.base_image_saver import BaseImageSaver
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class TiffSaver16bit(BaseImageSaver, CpuPlugin):
    """
    A class to save tomography data to tiff files
    :param pattern: How to slice the data. Default: 'VOLUME_XZ'.
    :param prefix: Override the default output tiff file prefix. Default: None.
    :param lower_threshold: The lower threshold for 16 bit conversion. \
    Default: -0.003
    :param upper_threshold: The upper threshold for 16 bit conversion. \
    Default: 0.005
    
    :config_warn: Do not use this plugin if the raw data is greater than \
    100 GB.
    """

    def __init__(self, name='TiffSaver16bit'):
        super(TiffSaver16bit, self).__init__(name)
        
    def pre_process(self):
        self.data_name = self.get_in_datasets()[0].get_name()
        self.count = 0
        self.group_name = self._get_group_name(self.data_name)
        self.folder = "%s/%s-%s" % (self.exp.meta_data.get("out_path"),
                                    self.name, self.data_name)
        if self.parameters['prefix']:
            self.filename = "%s/%s" % (self.folder, self.parameters['prefix'])
        else:
            self.filename = "%s/%s_" % (self.folder, self.data_name)
            self.filename += '%s_' % self.exp.meta_data.get("datafile_name")

        self.low_thresh = float(self.parameters['lower_threshold'])
        self.high_thresh = float(self.parameters['upper_threshold'])

        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
        
    def process_frames(self, data):
        frame = self.get_global_frame_index()[self.count]
        tmp = data[0]
        tmp[tmp < self.low_thresh] = self.low_thresh
        tmp[tmp > self.high_thresh] = self.high_thresh
        tmp = ((tmp - self.low_thresh) \
        / (self.high_thresh - self.low_thresh) * 65535).astype(np.uint16)
        filename = '%s_%05i.tiff' % (self.filename, frame)
        tf.imsave(filename, tmp)
        self.count += 1