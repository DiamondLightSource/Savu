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
.. module:: i18loader
   :platform: Unix
   :synopsis: A class for loading i18 data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging
import os
import numpy as np
from savu.plugins.base_loader import BaseLoader
import savu.test.test_utils as tu

from savu.plugins.utils import register_plugin


@register_plugin
class I18loader(BaseLoader):
    """
    A class to load tomography data from an xrd file
    """

    def __init__(self, name='I18loader'):
        super(I18loader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_str = '/entry1/cmos/data'
        print data_str
        data_obj = exp.create_data_object('in_data', 'xrd')
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get_meta_data("data_file"), 'r')
        data_obj.data = data_obj.backing_file[data_str]
        data_obj.set_shape(data_obj.data.shape)
#         data_obj, xrd_entry = self.multi_modal_setup('NXxrd', data_str)
        mono_energy = data_obj.backing_file['/entry1/instrument/DCM/energy'][0]
        self.exp.meta_data.set_meta_data("mono_energy", mono_energy)
        if '/entry1/instrument/raster_counterTimer01/I0' in data_obj.backing_file:
            control = np.expand_dims(data_obj.backing_file['/entry1/instrument/raster_counterTimer01/I0'].value,1)
        else:
            logging.debug("No monitor data found, filling this with ones instead")
            control = np.ones(data_obj.data.shape[:-2])
        # this is global since it is to do with the beam
        exp.meta_data.set_meta_data("control", control)
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'x.mm',
                                 'detector_x.mm',
                                 'detector_y.mm')

        rotation_angle = \
            data_obj.backing_file['/entry1/instrument/SampleMotors/sc_sample_thetafine'].value
        if rotation_angle.ndim > 1:
            rotation_angle = rotation_angle[:, 0]

        data_obj.meta_data.set_meta_data('rotation_angle', rotation_angle)
        print data_obj.data.shape
        data_obj.add_pattern("DIFFRACTION", core_dir=(2, 3),
                             slice_dir=(0, 1))
        data_obj.add_pattern("SINOGRAM", core_dir=(0, 1),
                             slice_dir=(3, 4))
        # this won't have projection yet
#         data_obj.add_pattern("PROJECTION", core_dir=(0, 2),
#                              slice_dir=(1, 3, 4))

