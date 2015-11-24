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
import numpy as np

import savu.data.data_structures as ds
from savu.core.utils import logmethod
from savu.plugins.base_loader import BaseLoader

from savu.plugins.utils import register_plugin


@register_plugin
class I12TomoLoader(BaseLoader):
    """
    A class to load i12 tomography data from a hdf5 file

    :param angular_spacing: Angular spacing between successive projections. Default: 0.2.
    :param dark: Path to the dark field data file. Default: '/dls/science/groups/das/ExampleData/i12/savu_data/ee12581-1_test/45657.nxs'. 
    :param flat: Path to the flat field data file. Default: '/dls/science/groups/das/ExampleData/i12/savu_data/ee12581-1_test/45658.nxs'.    
    """

    def __init__(self, name='I12TomoLoader'):
        super(I12TomoLoader, self).__init__(name)

    @logmethod
    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', 'tomo')
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

        logging.debug("Creating file '%s' '%s'", 'tomo_entry',
                      data_obj.backing_file.filename)

        data_obj.data = \
            data_obj.backing_file['entry/instrument/detector/data']

        dark_file = h5py.File(self.parameters['dark'], 'r')
        dark = dark_file['entry1/pco4000_dio_hdf/data']
        expInfo.set_meta_data('dark', dark[:].mean(0))

        flat_file = h5py.File(self.parameters['flat'], 'r')
        flat = flat_file['entry1/pco4000_dio_hdf/data']
        expInfo.set_meta_data('flat', flat[:].mean(0))

        data_obj.set_shape(data_obj.data.shape)
        self.set_data_reduction_params(data_obj)

    def data_mapping(self):
        exp = self.exp
        data_obj = exp.index['in_data']['tomo']
        data_obj.mapping = True
        mapping_obj = exp.create_data_object('mapping', 'tomo')

        angular_spacing = self.parameters['angular_spacing']
        rotation_angle = np.arange(0, 180+angular_spacing, angular_spacing)
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
