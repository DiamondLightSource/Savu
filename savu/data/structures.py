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


class RawTimeseriesData(object):
    """
    Descriptor for raw timeseries data
    """

    def __init__(self):
        super(RawTimeseriesData, self).__init__()
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
        f = h5py.File(path, 'r')
        self.data = f['entry1/tomo_entry/instrument/detector/data']
        self.image_key = f['entry1/tomo_entry/instrument/detector/image_key']
        self.rotation_angle = f['entry1/tomo_entry/sample/rotation_angle']
        self.control = f['entry1/tomo_entry/control/data']
        self.projection_axis = (1, 2)
        self.rotation_axis = (0,)


class ProjectionData(object):
    """
    Descriptor for corrected projection data
    """

    def __init__(self):
        super(ProjectionData, self).__init__()
        self.data = None
        self.data_avail = None
        self.rotation_angle = None
        self.rotation_angle_avail = None

    def create_backing_h5(self, path, plugin_name, data_shape, data_type,
                          rotation_angle_shape, rotation_angle_type, mpi=None):
        """
        Create a h5 backend for this ProjectionData
        :param path: The full path of the NeXus file to use as a backend
        :type path: str
        :param mpi: if an MPI process, provide MPI package here, default None
        :type mpi: package
        """
        f = None
        if mpi is None:
            f = h5py.File(path, 'w')
        else:
            f = h5py.File(path, 'w', driver='mpio', comm=mpi.COMM_WORLD)

        if f is None:
            raise IOError("Failed to open the hdf5 file")

        group = f.create_group(plugin_name)
        self.data = group.create_dataset('data', data_shape, data_type)
        self.data_avail = group.create_dataset('data_avail',
                                               data_shape, np.bool_)
        self.rotation_angle = \
            group.create_dataset('rotation_angle', rotation_angle_shape,
                                 rotation_angle_type)
        self.rotation_angle_avail = \
            group.create_dataset('rotation_angle_avail', data_shape, np.bool_)


class VolumeData(object):
    """
    Descriptor for volume data
    """

    def __init__(self):
        super(VolumeData, self).__init__()
        self.data = None
