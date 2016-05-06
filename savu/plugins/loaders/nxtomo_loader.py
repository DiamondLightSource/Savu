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
.. module:: nxtomo_loader
   :platform: Unix
   :synopsis: A class for loading standard tomography data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging
import numpy as np

from savu.plugins.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
from savu.data.data_structures.data_add_ons import TomoRaw


@register_plugin
class NxtomoLoader(BaseLoader):
    """
    A class to load i12 tomography data from a hdf5 file

    :param data_path: Path to the data inside the \
        file. Default: 'entry1/tomo_entry/data/data'.
    :param dark: Optional path to the dark field data file, nxs entry and \
        scale value. Default: [None, None, 1].
    :param flat: Optional Path to the flat field data file and path to data \
        in nxs file. Default: [None, None, 1].
    :param angles: A python statement to be evaluated or a file. Default: None.
    :param 3d_to_4d: Set to true if this reshape is required. Default: None.
    """

    def __init__(self, name='NxtomoLoader'):
        super(NxtomoLoader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', 'tomo')

        data_obj.backing_file = \
            h5py.File(self.exp.meta_data.get_meta_data("data_file"), 'r')

        data_obj.data = data_obj.backing_file[self.parameters['data_path']]

        self.__set_dark_and_flat(data_obj)
        n_angles = self.__set_rotation_angles(data_obj)

        if self.parameters['3d_to_4d']:
            if not self.parameters['angles']:
                raise Exception('Angles are required in the loader.')
            shape = self.__setup_3d_to_4d(data_obj, n_angles)
        elif len(data_obj.data.shape) is 3:
            shape = self.__setup_3d(data_obj)
        else:
            shape = self.__setup_4d(data_obj)

        try:
            control = data_obj.backing_file['entry1/tomo_entry/control/data']
            data_obj.meta_data.set_meta_data("control", control[...])
        except:
            logging.warn("No Control information available")

        self.__check_angles
        data_obj.set_shape(shape)
        self.set_data_reduction_params(data_obj)

    def __setup_3d(self, data_obj):
        logging.debug("Setting up 3d tomography data.")
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
        return data_obj.data.shape

    def __setup_3d_to_4d(self, data_obj, n_angles):
        logging.debug("setting up 4d tomography data from 3d input.")
        self.__setup_4d(data_obj)
        from savu.data.data_structures.data_type import Map_3d_to_4d_h5
        data_obj.data = Map_3d_to_4d_h5(data_obj.data, n_angles)
        return data_obj.data.get_shape()

    def __setup_4d(self, data_obj):
        logging.debug("setting up 4d tomography data.")
        rot = 0
        detY = 1
        detX = 2
        scan = 3

        data_obj.set_axis_labels('rotation_angle.degrees', 'detector_y.pixel',
                                 'detector_x.pixel', 'scan.number')

        data_obj.add_pattern('PROJECTION', core_dir=(detX, detY),
                             slice_dir=(rot, scan))
        data_obj.add_pattern('SINOGRAM', core_dir=(detX, rot),
                             slice_dir=(detY, scan))
        return data_obj.data.shape

    def __set_dark_and_flat(self, data_obj):
        flat = self.parameters['flat'][0]
        dark = self.parameters['dark'][0]

        if not flat or not dark:
            try:
                image_key = data_obj.backing_file[
                    'entry1/tomo_entry/instrument/detector/image_key']
                TomoRaw(data_obj)
                data_obj.get_tomo_raw().set_image_key(image_key[...])
            except KeyError:
                logging.warn("An image key was not found.")
                try:
                    mData = data_obj.mData
                    entry = 'entry1/tomo_entry/instrument/detector/flatfield'
                    mData.set_meta_data('flat', data_obj.backing_file[entry])
                    entry = 'entry1/tomo_entry/instrument/detector/darkfield'
                    mData.set_meta_data('dark', data_obj.backing_file[entry])
                except KeyError:
                    logging.warn("Dark and flat data was not found in input "
                                 "file.")
        if flat:
            self.__get_image('flat', 1, data_obj)
        if dark:
            self.__get_image('dark', 2, data_obj)

    def __get_image(self, name, key, data_obj):
        fpath, fentry, scale = self.parameters[name]
        h5file = h5py.File(fpath, 'r')
        try:
            image_key = \
                h5file['entry1/tomo_entry/instrument/detector/image_key']
            data = h5file[self.parameters['data_path']][
                image_key == key, ...].mean(0)*int(scale)
        except KeyError:
            data = h5file[fentry][...].mean(0)*int(scale)
        data_obj.meta_data.set_meta_data(name, data)

    def __set_rotation_angles(self, data_obj):
        angles = self.parameters['angles']

        if angles is None:
            try:
                entry = 'entry1/tomo_entry/data/rotation_angle'
                angles = data_obj.backing_file[entry][
                    (data_obj.meta_data.get_meta_data("image_key")) == 0, ...]
            except KeyError:
                logging.warn("No rotation angle entry found in input file.")
                angles = np.linspace(0, 180, data_obj.get_shape()[0])
        else:
            try:
                exec("angles = " + angles)
            except:
                try:
                    angles = np.loadtxt(angles)
                except:
                    raise Exception('Cannot set angles in loader.')
        data_obj.meta_data.set_meta_data("rotation_angle", angles)
        return len(angles)

    def __check_angles(self, data_obj, n_angles):
        data_angles = data_obj.data.get_shape()[0]
        if data_angles is not n_angles:
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s", n_angles, data_angles)
