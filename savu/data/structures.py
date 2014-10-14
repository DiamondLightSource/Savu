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
import logging

from mpi4py import MPI

NX_CLASS = 'NX_class'


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

    def __getattr__(self, name):
        """
        Delegate everything else to the data class
        """
        value = self.data.__getattribute__(name)
        return value


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


class PassThrough(object):
    """
    Interface Class describing when the input data of a plugin is also the
    output
    """

    def __init__(self):
        super(PassThrough, self).__init__()


class Data(object):
    """
    Baseclass for all data
    """

    def __init__(self):
        super(Data, self).__init__()
        self.backing_file = None
        self.data = None
        self.base_path = None

    def complete(self):
        """
        Closes the backing file and completes work
        """
        logging.debug("Completing file %s %s", self.base_path,
                      self.backing_file.filename)
        if self.backing_file is not None:
            self.backing_file.close()
            self.backing_file = None

    def external_link(self):
        return h5py.ExternalLink(self.backing_file.filename,
                                 self.base_path)


class RawTimeseriesData(Data):
    """
    Descriptor for raw timeseries data
    """

    def __init__(self):
        super(RawTimeseriesData, self).__init__()

        self.image_key = None
        self.rotation_angle = None
        self.control = None
        self.center_of_rotation = None
        self.projection_axis = (0, 0)
        self.rotation_axis = (0,)

    def populate_from_nexus(self, path):
        """
        Load a plugin.

        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        self.backing_file = h5py.File(path, 'r')
        logging.debug("Creating file '%s' '%s'", 'tomo_entry',
                      self.backing_file.filename)
        data = self.backing_file['entry1/tomo_entry/instrument/detector/data']
        self.data = SliceAlwaysAvailableWrapper(data)

        image_key = self.backing_file[
            'entry1/tomo_entry/instrument/detector/image_key']
        self.image_key = SliceAlwaysAvailableWrapper(image_key)

        rotation_angle = \
            self.backing_file['entry1/tomo_entry/sample/rotation_angle']
        self.rotation_angle = SliceAlwaysAvailableWrapper(rotation_angle)

        control = self.backing_file['entry1/tomo_entry/control/data']
        self.control = SliceAlwaysAvailableWrapper(control)

        self.projection_axis = (1, 2)
        self.rotation_axis = (0,)

    def create_backing_h5(self, path, group_name, data, mpi=False):
        """
        Create a h5 backend for this RawTimeseriesData

        :param path: The full path of the NeXus file to use as a backend
        :type path: str
        :param data: The structure from which this can be created
        :type data: savu.structure.RawTimeseriesData
        :param mpi: if an MPI process, provide MPI package here, default None
        :type mpi: package
        """
        self.backing_file = None
        if mpi:
            self.backing_file = h5py.File(path, 'w', driver='mpio',
                                          comm=MPI.COMM_WORLD)
        else:
            self.backing_file = h5py.File(path, 'w')

        if self.backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        logging.debug("Creating file '%s' '%s'", self.base_path,
                      self.backing_file.filename)

        self.base_path = group_name
        if not isinstance(data, RawTimeseriesData):
            raise ValueError("data is not a RawTimeseriesData")

        data_shape = data.data.shape
        data_type = np.double
        image_key_shape = data.image_key.shape
        image_key_type = data.image_key.dtype
        rotation_angle_shape = data.rotation_angle.shape
        rotation_angle_type = data.rotation_angle.dtype
        control_shape = data.control.shape
        control_type = data.control.dtype
        cor_shape = (data.data.shape[self.projection_axis[0]],)
        cor_type = np.double

        group = self.backing_file.create_group(group_name)
        group.attrs[NX_CLASS] = 'NXdata'
        data_value = group.create_dataset('data', data_shape, data_type)
        data_value.attrs['signal'] = 1
        data_avail = group.create_dataset('data_avail',
                                          data_shape, np.bool_)
        self.data = SliceAvailableWrapper(data_avail, data_value)

        # Create and prepopulate the following, as they are likely to be
        # Unchanged during the processing
        image_key = \
            group.create_dataset('image_key',
                                 image_key_shape, image_key_type)
        image_key_avail = \
            group.create_dataset('image_key_avail',
                                 image_key_shape, np.bool_)
        self.image_key = \
            SliceAvailableWrapper(image_key_avail, image_key)
        self.image_key[:] = data.image_key[:]

        rotation_angle = \
            group.create_dataset('rotation_angle',
                                 rotation_angle_shape, rotation_angle_type)
        rotation_angle_avail = \
            group.create_dataset('rotation_angle_avail',
                                 rotation_angle_shape, np.bool_)
        self.rotation_angle = \
            SliceAvailableWrapper(rotation_angle_avail, rotation_angle)
        self.rotation_angle[:] = data.rotation_angle[:]

        control = \
            group.create_dataset('control',
                                 control_shape, control_type)
        control_avail = \
            group.create_dataset('control_avail',
                                 control_shape, np.bool_)
        self.control = \
            SliceAvailableWrapper(control_avail, control)
        self.control[:] = data.control[:]

        cor = \
            group.create_dataset('center_of_rotation',
                                 cor_shape, cor_type)
        cor_avail = \
            group.create_dataset('center_of_rotation_avail',
                                 cor_shape, np.bool_)
        self.center_of_rotation = \
            SliceAvailableWrapper(cor_avail, cor)

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

    def get_clusterd_frame_list(self):
        """
        Gets a list of index arrays grouped by sequential image_key

        :returns: a list of integer index arrays
        """
        diff = np.abs(np.diff(self.image_key))
        pos = np.where(diff > 0)[0] + 1
        return np.split(np.arange(self.image_key.shape[0]), pos)


class ProjectionData(Data):
    """
    Descriptor for corrected projection data
    """

    def __init__(self):
        super(ProjectionData, self).__init__()
        self.rotation_angle = None
        self.center_of_rotation = None

    def create_backing_h5(self, path, group_name, data, mpi=False):
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
        if mpi:
            self.backing_file = h5py.File(path, 'w', driver='mpio',
                                          comm=MPI.COMM_WORLD)
        else:
            self.backing_file = h5py.File(path, 'w')

        if self.backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        self.base_path = group_name
        logging.debug("Creating file '%s' '%s'", self.base_path,
                      self.backing_file.filename)

        data_shape = None
        data_type = None
        rotation_angle_shape = None
        rotation_angle_type = None
        cor_shape = None
        cor_type = np.double

        if data.__class__ == RawTimeseriesData:
            data_shape = (data.get_number_of_projections(),) +\
                data.get_projection_shape()
            data_type = np.double
            rotation_angle_shape = (data.get_number_of_projections(),)
            rotation_angle_type = data.rotation_angle.dtype
            cor_shape = (data.data.shape[1],)

        elif data.__class__ == ProjectionData:
            data_shape = data.data.shape
            data_type = np.double
            rotation_angle_shape = data.rotation_angle.shape
            rotation_angle_type = data.rotation_angle.dtype
            cor_shape = (data.data.shape[1],)

        group = self.backing_file.create_group(group_name)
        group.attrs[NX_CLASS] = 'NXdata'
        data_value = group.create_dataset('data', data_shape, data_type)
        data_value.attrs['signal'] = 1
        data_avail = group.create_dataset('data_avail',
                                          data_shape, np.bool_)
        self.data = SliceAvailableWrapper(data_avail, data_value)

        rotation_angle = \
            group.create_dataset('rotation_angle',
                                 rotation_angle_shape, rotation_angle_type)
        rotation_angle_avail = \
            group.create_dataset('rotation_angle_avail',
                                 rotation_angle_shape, np.bool_)
        self.rotation_angle = \
            SliceAvailableWrapper(rotation_angle_avail, rotation_angle)

        cor = \
            group.create_dataset('center_of_rotation',
                                 cor_shape, cor_type)
        cor_avail = \
            group.create_dataset('center_of_rotation_avail',
                                 cor_shape, np.bool_)
        self.center_of_rotation = \
            SliceAvailableWrapper(cor_avail, cor)

    def populate_from_h5(self, path):
        """
        Populate the contents of this object from a file

        :param path: The full path of the h5 file to load.
        :type path: str
        """
        self.backing_file = h5py.File(path, 'r')

        logging.debug("Creating file '%s' '%s'", 'TimeseriesFieldCorrections',
                      self.backing_file.filename)

        data = self.backing_file['TimeseriesFieldCorrections/data']
        self.data = SliceAlwaysAvailableWrapper(data)

        rotation_angle = \
            self.backing_file['TimeseriesFieldCorrections/rotation_angle']
        self.rotation_angle = SliceAlwaysAvailableWrapper(rotation_angle)

    def get_number_of_sinograms(self):
        """
        Gets the real number sinograms

        :returns: integer number of sinogram frames
        """
        return self.data.shape[1]

    def get_number_of_projections(self):
        """
        Gets the real number projections

        :returns: integer number of projection frames
        """
        return self.data.shape[0]

    def get_data_shape(self):
        """
        Gets the real number projections

        :returns: integer number of projection frames
        """
        return self.data.shape


class VolumeData(Data):
    """
    Descriptor for volume data
    """

    def __init__(self):
        super(VolumeData, self).__init__()

    def create_backing_h5(self, path, group_name, data_shape,
                          data_type, mpi=False):
        """
        Create a h5 backend for this ProjectionData

        :param path: The full path of the NeXus file to use as a backend
        :type path: str
        :param data_shape: The shape of the data block
        :type data: tuple
        :param data_type: The type of the data block
        :type data: np.dtype
        :param mpi: if an MPI process, provide MPI package here, default None
        :type mpi: package
        """
        self.backing_file = None
        if mpi:
            self.backing_file = h5py.File(path, 'w', driver='mpio',
                                          comm=MPI.COMM_WORLD)
        else:
            self.backing_file = h5py.File(path, 'w')

        if self.backing_file is None:
            raise IOError("Failed to open the hdf5 file")

        self.base_path = group_name
        logging.debug("Creating file '%s' '%s'", self.base_path,
                      self.backing_file.filename)

        group = self.backing_file.create_group(group_name)
        group.attrs[NX_CLASS] = 'NXdata'
        data_value = group.create_dataset('data', data_shape, data_type)
        data_value.attrs['signal'] = 1
        data_avail = group.create_dataset('data_avail',
                                          data_shape, np.bool_)
        self.data = SliceAvailableWrapper(data_avail, data_value)

    def get_volume_shape(self):
        """
        Gets the real number sinograms

        :returns: integer number of sinogram frames
        """
        return self.data.shape
