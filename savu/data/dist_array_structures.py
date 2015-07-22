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

from savu.core.utils import logmethod

NX_CLASS = 'NX_class'

# Core Direction Keywords
CD_PROJECTION = 'core_dir_projection'# What axes will my projection shape be?
CD_SINOGRAM = 'core_dir_sinogram'# What axes will the sinogram be along?
CD_ROTATION_AXIS = 'core_dir_rotation_axis'# What axes will look down the rotation axis?
CD_PATTERN = 'core_dir_pattern'# What axis looks down the pattern axis?


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

    @logmethod
    def __getitem__(self, item):
        return self.data[item]

    @logmethod
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
        self.core_directions = {}
        self.current_dist = None # for DistArray

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

    def external_link(self):
        return h5py.ExternalLink(self.backing_file.filename,
                                 self.base_path)

    def get_slice_list(self, frame_type):
        if frame_type in self.core_directions.keys():
            it = np.nditer(self.data, flags=['multi_index'])
            dirs_to_remove = list(self.core_directions[frame_type])
            dirs_to_remove.sort(reverse=True)
            for direction in dirs_to_remove:
                it.remove_axis(direction)
            mapping_list = range(len(it.multi_index))
            dirs_to_remove.sort()
            for direction in dirs_to_remove:
                mapping_list.insert(direction, -1)
            mapping_array = np.array(mapping_list)
            slice_list = []
            while not it.finished:
                tup = it.multi_index + (slice(None),)
                slice_list.append(tuple(np.array(tup)[mapping_array]))
                it.iternext()
            return slice_list
        return None

    def get_data_shape(self):
        """
        Simply returns the shape of the main data array
        """
        return self.data.shape



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

    @logmethod
    def populate_from_nx_tomo(self, path):
        """
        Populate the RawTimeseriesData from an NXTomo defined NeXus file

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

        self.core_directions[CD_PROJECTION] = (1, 2)
        self.core_directions[CD_SINOGRAM] = (0, 2)
        self.core_directions[CD_ROTATION_AXIS] = (0, )


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

    @logmethod
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

        self.core_directions[CD_PROJECTION] = (1, 2)
        self.core_directions[CD_SINOGRAM] = (0, 2)
        self.core_directions[CD_ROTATION_AXIS] = (0,)

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


class VolumeData(Data):
    """
    Descriptor for volume data
    """

    def __init__(self):
        super(VolumeData, self).__init__()


    def get_volume_shape(self):
        """
        Gets the real number sinograms

        :returns: integer number of sinogram frames
        """
        return self.data.shape
