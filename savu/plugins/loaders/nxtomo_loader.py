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
.. module:: tomography_loader
   :platform: Unix
   :synopsis: A class for loading tomography data using the standard loaders
   library.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging

import savu.data.data_structures as ds
from savu.core.utils import logmethod
from savu.plugins.base_loader import BaseLoader

from savu.plugins.utils import register_plugin


@register_plugin
class NxtomoLoader(BaseLoader):
    """
    A class to load tomography data from an NXTomo file
    """

    def __init__(self, name='NxtomoLoader'):
        super(NxtomoLoader, self).__init__(name)

    @logmethod
    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', 'tomo')
        ds.TomoRaw(data_obj)

        # from nexus file determine rotation angle
        rot = 0
        detY = 1
        detX = 2
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'detector_y.pixel',
                                 'detector_x.pixel')

        data_obj.add_pattern('PROJECTION', core_dir=(detX, detY),
                             slice_dir=(rot,))
        data_obj.add_pattern('SINOGRAM', core_dir=(detX, rot),
                             slice_dir=(detY,))

        objInfo = data_obj.meta_data
        expInfo = exp.meta_data

        data_obj.backing_file = \
            h5py.File(expInfo.get_meta_data("data_file"), 'r')

        logging.debug("Creating file '%s' '%s'", 'tomo_entry',
                      data_obj.backing_file.filename)

        data_obj.data = data_obj.backing_file['entry1/tomo_entry/data/data']

        image_key = data_obj.backing_file[
            'entry1/tomo_entry/instrument/detector/''image_key']

        data_obj.get_tomo_raw().set_image_key(image_key[...])

        rotation_angle = \
            data_obj.backing_file['entry1/tomo_entry/data/rotation_angle']
        objInfo.set_meta_data("rotation_angle", rotation_angle
                              [(objInfo.get_meta_data("image_key")) == 0, ...])

        try:
            control = data_obj.backing_file['entry1/tomo_entry/control/data']
            objInfo.set_meta_data("control", control[...])
        except:
            logging.warn("No Control information available")

        data_obj.set_shape(data_obj.data.shape)
