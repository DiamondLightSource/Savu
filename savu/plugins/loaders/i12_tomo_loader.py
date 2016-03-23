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
.. module:: i12_tomo_loader
   :platform: Unix
   :synopsis: A class for loading i12 mutli-scan tomography data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging
import numpy as np
import os

import savu.data.data_structures as ds
from savu.plugins.base_loader import BaseLoader
import savu.test.test_utils as tu

from savu.plugins.utils import register_plugin


@register_plugin
class I12TomoLoader(BaseLoader):
    """
    A class to load i12 tomography data from a hdf5 file

    :param angular_spacing: Angular spacing between successive \
        projections. Default: 0.2.
    :param data_path: Path to the data inside the \
        file. Default: 'entry1/tomo_entry/data/data'.
    :param dark: Path to the dark field data \
        file. Default: 'Savu/test_data/data/i12_test_data/45657.nxs'.
    :param flat: Path to the flat field data \
        file. Default: 'Savu/test_data/data/i12_test_data/45658.nxs'.
    :param flat_dark_path: Path to the data inside the \
        file. Default: 'entry1/data/pco4000_dio_hdf/data'
    """

    def __init__(self, name='I12TomoLoader'):
        super(I12TomoLoader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp._create_data_object('in_data', 'tomo')
        ds.TomoRaw(data_obj)

        # from nexus file determine rotation angle
        frame = 0
        detY = 1
        detX = 2

        data_obj.set_axis_labels('frame.number',
                                 'detector_y.pixel',
                                 'detector_x.pixel')

        data_obj.add_pattern('PROJECTION', core_dir=(detX, detY),
                             slice_dir=(frame,))
        expInfo = exp.meta_data

        data_obj.backing_file = \
            h5py.File(expInfo.get_meta_data("data_file"), 'r')

        logging.debug("Opened file '%s' '%s'", 'tomo_entry',
                      data_obj.backing_file.filename)

        logging.debug("Getting the path to the data")

        data_obj.data = \
            data_obj.backing_file[self.parameters['data_path']]

        logging.debug("Getting the path to the dark data")

        dark_file = h5py.File(self.get_file_path('dark'), 'r')
        dark = dark_file[self.parameters['flat_dark_path']]
        expInfo.set_meta_data('dark', dark[:].mean(0))

        logging.debug("Getting the path to the flat data")
        flat_file = h5py.File(self.get_file_path('flat'), 'r')
        flat = flat_file[self.parameters['flat_dark_path']]
        expInfo.set_meta_data('flat', flat[:].mean(0))

        data_obj.set_shape(data_obj.data.shape)
        self.set_data_reduction_params(data_obj)

    def data_mapping(self):
        exp = self.exp
        data_obj = exp.index['in_data']['tomo']
        data_obj.mapping = True
        mapping_obj = exp.create_data_object('mapping', 'tomo')

        angular_spacing = self.parameters['angular_spacing']

        # use this if scaning [0, 180]
        n_angles = int(np.ceil((180+angular_spacing)/float(angular_spacing)))

        # use this if scaning [0, 180)
        # n_angles = int(np.ceil((180)/float(angular_spacing)))

        rotation_angle = np.linspace(0, 180, n_angles)

        mapping_obj.set_axis_labels('rotation_angle.degrees',
                                    'detector_y.pixel',
                                    'detector_x.pixel',
                                    'scan.number')

        rot = 0
        detY = 1
        detX = 2
        scan = 3

        mapping_obj.meta_data.set_meta_data('rotation_angle', rotation_angle)

        mapping_obj.add_pattern('PROJECTION', core_dir=(detX, detY),
                                slice_dir=(rot, scan))

        mapping_obj.add_pattern('SINOGRAM', core_dir=(detX, rot),
                                slice_dir=(detY, scan))

        loaded_shape = data_obj.get_shape()
        n_scans = loaded_shape[0]/len(rotation_angle)
        shape = (rotation_angle.shape + loaded_shape[1:3] + (n_scans,))

        mapping_obj.set_shape(shape)

    def get_file_path(self, name):
        path = self.parameters[name]
        if path.split(os.sep)[0] == 'Savu':
            path = tu.get_test_data_path(path.split('/test_data/data')[1])
            self.parameters['flat_dark_path'] = 'entry/final_result_tomo/data'
        return path
