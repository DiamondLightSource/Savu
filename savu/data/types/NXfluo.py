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
.. module:: NXfluo
   :platform: Unix
   :synopsis: Class which describes the NXfluo data structure

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import h5py
import logging
import numpy as np

from savu.data.DataInterface import DataInterface
from savu.data.structures import CD_PROJECTION, CD_PATTERN

from savu.core.utils import logmethod


class RawTimeseriesData(DataInterface):
    """
    Descriptor for NXfluo data type
    """

    def __init__(self):
        super(RawTimeseriesData, self).__init__()
        self.backing_file = None
        self.data = None
        self.base_path = None
        self.core_directions = {}

        self.energy = None
        self.data = None
        self.x = None
        self.y = None
        self.monitor = None
        self.data_shape = None
        self.mono_energy = None
    @logmethod
    def complete(self):
        """
        Closes the backing file and completes work
        """
        if self.backing_file is not None:
            logging.debug("Completing file %s %s", self.base_path,
                          self.backing_file.filename)
            self.backing_file.close()
            self.backing_file = None

    @logmethod
    def load_from_file(self, path):
        """
        Populate the RawTimeseriesData from an NXFluo defined NeXus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        self.backing_file = h5py.File(path, 'r')
        logging.debug("Creating file '%s' '%s'", 'fluo_entry',
                      self.backing_file.filename)

        self.data = self.backing_file[
            'entry1/fluo_entry/data/data']

        self.energy = self.backing_file[
            'entry1/fluo_entry/data/energy']

        self.x = self.backing_file[
            'entry1/fluo_entry/data/x']

        self.y = self.backing_file[
            'entry1/fluo_entry/data/y']

        self.monitor = self.backing_file[
            'entry1/fluo_entry/monitor/data']
        self.mono = self.backing_file[
            'entry1/fluo_entry/instrument/monochromator/energy']
        
        self.core_directions[CD_PROJECTION] = (0, 1)
        self.core_directions[CD_PATTERN] = (2, )

    def link_to_transport_mechanism(self, transport):
        """
        Create a h5 backend for this RawTimeseriesData

        :param path: The full path of the NeXus file to use as a backend
        :type path: str
        :param data: The structure from which this can be created
        :type data: savu.structure.RawTimeseriesData
        :param mpi: if an MPI process, provide MPI package here, default None
        :type mpi: package
        """

        self.core_directions[CD_PROJECTION] = (0, 1)
        self.core_directions[CD_PATTERN] = (2, )
        #TODO need to sort out data shape
        data_shape = self.data_shape
        if data_shape is None:
            data_shape = self.data.data.shape
        data_type = np.double
        energy_shape = self.data.energy.shape# energy axis
        energy_type = self.data.energy.dtype
        x_shape = self.data.x.shape#first translation axis
        x_type = self.data.x.dtype
        y_shape = self.data.x.shape#y translation axis
        y_type = self.data.x.dtype
        monitor_shape = self.data.monitor.shape# I0
        monitor_type = self.data.monitor.dtype
        mono_shape = self.data.mono.shape
        mono_type = self.data.mono.dtype

        self.data = transport.add_data_block(
            'data', data_shape, data_type)
        self.energy = transport.add_data_block(
            'energy', energy_shape, energy_type)
        self.x = transport.add_data_block(
            'x', x_shape, x_type)
        self.y = transport.add_data_block(
            'y', y_shape, y_type)
        self.monitor = transport.add_data_block(
            'monitor', monitor_shape, monitor_type)
        self.mono = transport.add_data_block(
            'mono', mono_shape, mono_type)
        return
