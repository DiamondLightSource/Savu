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
.. module:: base_image_saver
   :platform: Unix
   :synopsis: Handles common functionality for savers that save separate image files.

.. moduleauthor:: Dan Nixon <daniel.nixon@stfc.ac.uk>

"""

from mpi4py import MPI
import os

from savu.plugins.savers.base_saver import BaseSaver
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


class BaseImageSaver(BaseSaver, CpuPlugin):
    def __init__(self, name):
        super(BaseImageSaver, self).__init__(name)
        self.count = None
        self.folder = None
        self.data_name = None
        self.file_name = None
        self.group_name = None
        self.max_files = 100000

    def pre_process(self):
        self.data_name = self.get_in_datasets()[0].get_name()
        self.count = 0
        self.group_name = self._get_group_name(self.data_name)
        self.folder = "%s/%s_" % (self.exp.meta_data.get("out_path"),
                                    self.name)
        self.folder = self.folder + str(self.exp.meta_data.get('nPlugin'))
        if self.parameters['prefix']:
            self.filename = "%s/%s" % (self.folder, self.parameters['prefix'])
        else:
            self.filename = "%s/%s_" % (self.folder, "img")
            self.filename += '%s_' % self.exp.meta_data.get("datafile_name")

        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

    def setup(self):
        super(BaseImageSaver, self).setup()
        in_pData = self.get_plugin_in_datasets()[0]
        if in_pData.get_total_frames() > self.max_files:
            emsg = "Sorry, your data is too big to use an image saver."
            raise Exception(emsg)
