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
.. module:: mrc_saver
   :platform: Unix
   :synopsis: Saves data as .mrc file

.. moduleauthor:: Elaine Ho <Elaine.Ho@rfi.ac.uk>
"""
from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin
# Import any additional libraries or base plugins here.
import os
import mrcfile
import logging

from savu.plugins.savers.base_image_saver import BaseImageSaver
from savu.plugins.driver.cpu_plugin import CpuPlugin
import savu.core.utils as cu

# This decorator is required for the configurator to recognise the plugin
@register_plugin
class MrcSaver(BaseImageSaver, CpuPlugin):
# Each class must inherit from the Plugin class and a driver

    def __init__(self):
        super(MrcSaver, self).__init__("MrcSaver")
        self.in_data = None
        self.filename = None

    def pre_process(self):
        # Get metadata to create mrc file
        self.in_data = self.get_in_datasets()[0]
        filename = self.__get_file_name()
        data_type_lookup = {'int8': 0, 'int16': 1, 'float32':2, 'complex64':4, 'uint16':6}
        try:
            mrc_mode = data_type_lookup[self.parameters['mrc_mode']]
        except:
            msg = "Mrc mode must be one of {}, "\
                "defaulting to uint16".format(list(data_type_lookup.keys()))
            mrc_mode = data_type_lookup['uint16']
            logging.warning(msg)
            cu.user_message(msg)

        # Create mrc file
        self.mrc = mrcfile.new_mmap(
            name=filename,
            shape=self.in_data.get_shape(),
            mrc_mode=mrc_mode,
        )
        logging.info("Created mrc file {}".format(self.filename))

    def process_frames(self, data):
        # Save data to mrc in parallel
        idx = self.get_current_slice_list()[0]
        self.mrc.data[idx] = data[0]
        logging.debug("Processed frame {}".format(idx[0]))

    def post_process(self):
        # Close mrc file
        self.mrc.close()
        logging.info("MRC file closed")

    def __get_file_name(self):
        # Get the mrc filename in the format <original_img_name>_processed.mrc
        out_path = self.exp.meta_data.get('out_path')
        imgname = os.path.splitext(os.path.split(self.exp.meta_data.get('data_file'))[-1])[0]
        fname = "{}_processed.mrc".format(imgname)
        return os.path.join(out_path, fname)
