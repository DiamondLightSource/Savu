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
.. module:: structures
   :platform: Unix
   :synopsis: Classes which describe the main data types for passing between
              plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
import h5py


class SliceAvailableWrapper(object):
    """
    This class takes 2 datasets, one avaialble boolean ndarray, and 1 data
    ndarray.  Its purpose is to provide slices from the data array only if data
    has been put there, and to allow a convinient way to put slices into the
    data array, and set the available array to True
    """
    def __init__(self, avail, data):
        """
        :param avail: The available boolean ndArray
        :type avail: boolean ndArray
        :param data: The data ndArray
        :type data: any ndArray
        """
        self.avail = avail
        self.data = data

    def __getitem__(self, item):
        if self.avail[item].all():
            return self.data[item]
        else:
            return None

    def __setitem__(self, item, value):
        self.data[item] = value
        self.avail[item] = True


class SliceAlwaysAvailableWrapper(SliceAvailableWrapper):
    """
    This class takes 1 data ndarray.  Its purpose is to provide slices from the
    data array in the same way as the SliceAvailableWrapper but assuming the
    data is always available (for example in the case of the input file)
    """
    def __init__(self, data):
        """
        :param data: The data ndArray
        :type data: any ndArray
        """
        super(SliceAlwaysAvailableWrapper, self).__init__(None, data)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value


class RawTimeseriesData(object):
    """
    Descriptor for raw timeseries data
    """

    def __init__(self):
        super(RawTimeseriesData, self).__init__()
        self.nexus_file = None

        self.data = None
        self.image_key = None
        self.rotation_angle = None
        self.control = None
        self.projection_axis = (0, 0)
        self.rotation_axis = (0,)

    def populate_from_nexus(self, path):
        """
        Load a plugin.
        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        self.nexus_file = h5py.File(path, 'r')
        data = self.nexus_file['entry1/tomo_entry/instrument/detector/data']
        self.data = SliceAlwaysAvailableWrapper(data)

        image_key = \
            self.nexus_file['entry1/tomo_entry/instrument/detector/image_key']
        self.image_key = SliceAlwaysAvailableWrapper(image_key)

        rotation_angle = \
            self.nexus_file['entry1/tomo_entry/sample/rotation_angle']
        self.rotation_angle = SliceAlwaysAvailableWrapper(rotation_angle)

        control = self.nexus_file['entry1/tomo_entry/control/data']
        self.control = SliceAlwaysAvailableWrapper(control)

        self.projection_axis = (1, 2)
        self.rotation_axis = (0,)

    def get_number_of_projections(self):
        """
        Gets the real number of projections excluding calibration data
        :returns: integer number of data frames
        """
        return (self.image_key.data[:] == 0).sum()

    def get_projection_shape(self):
        """
        Gets the shape of a projection
        :returns: a tuple of the shape of a single projection
        """
        return self.data.data.shape[1:3]

    def complete(self):
        """
        Closes the backing file and completes work
        """
        if self.nexus_file is not None:
            self.nexus_file.close()
            self.nexus_file = None


class ProjectionData(object):
    """
    Descriptor for corrected projection data
    """

    def __init__(self):
        super(ProjectionData, self).__init__()
        self.backing_file = None

        self.data = None
        self.rotation_angle = None

    def create_backing_h5(self, path, plugin_name, data, mpi=None):
        """
        Create a h5 backend for this ProjectionData
        :param path: The full path of the NeXus file to use as a backend
        :type path: str
        :param data: The structure from which this can be created
        :type data: savu.structure
        :param mpi: if an MPI process, provide MPI package here, default None
        :type mpi: package
        """
        self.backing_file = None
        if mpi is None:
            self.backing_file = h5py.File(path, 'w')
        else:
            self.backing_file = h5py.File(path, 'w', driver='mpio',
                                          comm=mpi.COMM_WORLD)

        if self.backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        data_shape = None
        data_type = None
        rotation_angle_shape = None
        rotation_angle_type = None

        if data.__class__ == RawTimeseriesData:
            data_shape = (data.get_number_of_projections(),) +\
                data.get_projection_shape()
            data_type = np.double
            rotation_angle_shape = (data.get_number_of_projections(),)
            rotation_angle_type = data.rotation_angle.data.dtype

        elif data.__class__ == ProjectionData:
            data_shape = data.data.shape()
            data_type = np.double
            rotation_angle_shape = data.rotation_angle.data.shape
            rotation_angle_type = data.rotation_angle.data.dtype

        group = self.backing_file.create_group(plugin_name)
        data = group.create_dataset('data', data_shape, data_type)
        data_avail = group.create_dataset('data_avail',
                                          data_shape, np.bool_)
        self.data = SliceAvailableWrapper(data_avail, data)

        rotation_angle = \
            group.create_dataset('rotation_angle',
                                 rotation_angle_shape, rotation_angle_type)
        rotation_angle_avail = \
            group.create_dataset('rotation_angle_avail',
                                 rotation_angle_shape, np.bool_)
        self.rotation_angle = \
            SliceAvailableWrapper(rotation_angle_avail, rotation_angle)

    def complete(self):
        """
        Closes the backing file and completes work
        """
        if self.backing_file is not None:
            self.backing_file.close()
            self.backing_file = None


class VolumeData(object):
    """
    Descriptor for volume data
    """

    def __init__(self):
        super(VolumeData, self).__init__()
        self.data = None
