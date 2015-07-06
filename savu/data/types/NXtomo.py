# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: NXtomo
   :platform: Unix
   :synopsis: Class which describes the NXtomo data structure

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import h5py
import logging
import numpy as np

from savu.data.DataInterface import DataInterface
from savu.data.structures import CD_PROJECTION
from savu.data.structures import CD_ROTATION_AXIS, CD_SINOGRAM

from savu.core.utils import logmethod


class RawTimeseriesData(DataInterface):
    """
    Descriptor for NXtomo data type
    """

    def __init__(self):
        super(RawTimeseriesData, self).__init__()
        self.backing_file = None
        self.data = None
        self.base_path = None
        self.core_directions = {}

        self.image_key = None
        self.rotation_angle = None
        self.control = None
        self.center_of_rotation = None

        self.data_shape = None

    @logmethod
    def link_to_file(self, path):
        """
        Populate the RawTimeseriesData from an NXTomo defined NeXus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        self.backing_file = h5py.File(path, 'r')
        logging.debug("Creating file '%s' '%s'", 'tomo_entry',
                      self.backing_file.filename)

        self.data = self.backing_file[
            'entry1/tomo_entry/instrument/detector/data']

        self.image_key = self.backing_file[
            'entry1/tomo_entry/instrument/detector/image_key']

        self.rotation_angle = self.backing_file[
            'entry1/tomo_entry/sample/rotation_angle']

        self.control = self.backing_file[
            'entry1/tomo_entry/control/data']

        self.core_directions[CD_PROJECTION] = (1, 2)
        self.core_directions[CD_SINOGRAM] = (0, 2)
        self.core_directions[CD_ROTATION_AXIS] = (0, )

    @logmethod
    def complete(self):
        """
        Closes the backing file and completes work if required
        """
        if self.backing_file is not None:
            logging.debug("Completing file %s %s", self.base_path,
                          self.backing_file.filename)
            self.backing_file.close()
            self.backing_file = None

    def link_to_transport_mechanism(self, transport):
        """
        Create a transport backend for the NXTomo standard.

        :param path: The full path of the NeXus file to use as a backend
        :type path: str
        :param data: The structure from which this can be created
        :type data: savu.structure.RawTimeseriesData
        :param mpi: if an MPI process, provide MPI package here, default None
        :type mpi: package
        """

        self.core_directions[CD_PROJECTION] = (1, 2)
        self.core_directions[CD_SINOGRAM] = (0, 2)
        self.core_directions[CD_ROTATION_AXIS] = 0

        #TODO need to sort out data shape
        data_shape = self.data_shape
        if data_shape is None:
            data_shape = self.data.data.shape
        data_type = np.double
        image_key_shape = self.data.image_key.shape
        image_key_type = self.data.image_key.dtype
        rotation_angle_shape = self.data.rotation_angle.shape
        rotation_angle_type = self.data.rotation_angle.dtype
        control_shape = self.data.control.shape
        control_type = self.data.control.dtype
        cor_shape = (self.data.data.shape[
            self.core_directions[CD_ROTATION_AXIS]],)
        cor_type = np.double

        self.data = transport.add_data_block(
            'data', data_shape, data_type)
        self.image_key = transport.add_data_block(
            'image_key', image_key_shape, image_key_type)
        self.rotation_angle = transport.add_data_block(
            'rotation_angle', rotation_angle_shape, rotation_angle_type)
        self.control = transport.add_data_block(
            'control', control_shape, control_type)
        self.center_of_rotation = transport.add_data_block(
            'center_of_rotation', cor_shape, cor_type)

        return
