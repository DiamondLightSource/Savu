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
.. module:: extended_tiff_saver
   :platform: Unix
   :synopsis: A class to save output in tiff format

.. moduleauthor:: Malte Storm <malte.storm@diamond.ac.uk>

"""

from mpi4py import MPI
import tifffile as tf
import os

from savu.plugins.savers.base_saver import BaseSaver
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class ExtendedTiffSaver(BaseSaver, CpuPlugin):
    """
    A class to save tomography data to tiff files
    :param pattern: How to slice the data. Default: 'VOLUME_XZ'.
    :param use_name_leading_zeros: If enabled, the slice numbering will be \
    written as a %05i pattern. Default: False.
    :param use_scan_number: If enabled, the scan number will be added to the \
    output filename. Default: False
    :config_warn: Do not use this plugin if the raw data is greater than \
    100 GB.
    """

    def __init__(self, name='ExtendedTiffSaver'):
        super(ExtendedTiffSaver, self).__init__(name)
        self.count = None
        self.folder = None
        self.data_name = None
        self.file_name = None
        self.group_name = None

    def pre_process(self):
        self.data_name = self.get_in_datasets()[0].get_name()
        self.count = 0
        self.group_name = self._get_group_name(self.data_name)
        self.folder = "%s/%s-%s" % (self.exp.meta_data.get("out_path"),
                                    self.name, self.data_name)
        self.filename = "%s/%s_" % (self.folder, self.data_name)
        
        self.use_zero_padding = self.parameters['use_name_leading_zeros']
        self.use_scan_number = self.parameters['use_scan_number']
        if self.use_scan_number:
            self.filename += '%s_' \
            %self.exp.meta_data.get("out_path").split('/')[-1].split('_')[1]
        if self.use_zero_padding:
            self.name_appendix = '%05i.tiff'
        else:
            self.name_appendix = '%i.tiff'
        
        
        
        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

    def process_frames(self, data):
        frame = self.get_global_frame_index()[0][self.count]
        filename = self.filename + self.name_appendix %frame
        tf.imsave(filename, data[0])
        self.count += 1
