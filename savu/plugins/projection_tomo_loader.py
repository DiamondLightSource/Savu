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
.. module:: projection_tomo_loader
   :platform: Unix
   :synopsis: A class for loading tomography data that is already calibrated
   and normalised (i.e. projection data not raw data)

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import h5py

from savu.core.utils import logmethod
from savu.plugins.base_loader import BaseLoader

from savu.plugins.utils import register_plugin


@register_plugin
class ProjectionTomoLoader(BaseLoader):
    """
    A class to load tomography data from an NXTomo file
    """

    def __init__(self, name='ProjectionTomoLoader'):
        super(ProjectionTomoLoader, self).__init__(name)

    @logmethod
    def setup(self):

        data_obj = self.exp.create_data_object("in_data", "tomo")
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
        expInfo = self.exp.meta_data

        data_obj.backing_file = \
            h5py.File(expInfo.get_meta_data("data_file"), 'r')
        logging.debug("Creating file '%s' '%s'", 'tomo_entry',
                      data_obj.backing_file.filename)

        data_obj.data = \
            data_obj.backing_file['TimeseriesFieldCorrections/data']

        rotation_angle = \
            data_obj.backing_file['TimeseriesFieldCorrections/rotation_angle']
        objInfo.set_meta_data("rotation_angle", rotation_angle[...])

        data_obj.set_shape(data_obj.data.shape)
