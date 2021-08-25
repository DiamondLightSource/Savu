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
.. module:: p2r_fly_scan_detector_loader
   :platform: Unix
   :synopsis: A class for loading p2r fly scan detector data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging
import numpy as np

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
import savu.core.utils as cu
from savu.data.data_structures.data_types.map_3dto4d_h5 import Map3dto4dh5
from savu.data.data_structures.data_types.data_plus_darks_and_flats \
    import ImageKey, NoImageKey



#@register_plugin
class P2rFlyScanDetectorLoader(BaseLoader):
    def __init__(self, name='P2rFlyScanDetectorLoader'):
        super(P2rFlyScanDetectorLoader, self).__init__(name)

    def setup(self):
        exp = self.exp

        data_obj = exp.create_data_object('in_data', 'tomo')

        data_obj.backing_file = \
            h5py.File(self.exp.meta_data.get("data_file"), 'r')

        data_obj.data = data_obj.backing_file[self.parameters['data_path']]

        self.__set_dark_and_flat(data_obj)

        if self.parameters['3d_to_4d']:
            if not self.parameters['angles']:
                raise Exception('Angles are required in the loader.')
            self.__setup_4d(data_obj)
            n_angles = self.__set_rotation_angles(data_obj)
            shape = self.__setup_3d_to_4d(data_obj, n_angles)
        else:
            if len(data_obj.data.shape) == 3:
                shape = self._setup_3d(data_obj)
            else:
                shape = self.__setup_4d(data_obj)
            self.__set_rotation_angles(data_obj)

        try:
            control = data_obj.backing_file['entry1/tomo_entry/control/data']
            data_obj.meta_data.set("control", control[...])
        except:
            logging.warning("No Control information available")

        nAngles = len(data_obj.meta_data.get('rotation_angle'))
        self.__check_angles(data_obj, nAngles)
        data_obj.set_original_shape(shape)
        self.set_data_reduction_params(data_obj)
        data_obj.data._set_dark_and_flat()

    def _setup_3d(self, data_obj):
        logging.debug("Setting up 3d tomography data.")
        rot = 0
        detY = 1
        detX = 2
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'detector_y.pixel',
                                 'detector_x.pixel')

        data_obj.add_pattern('PROJECTION', core_dims=(detX, detY),
                             slice_dims=(rot,))
        data_obj.add_pattern('SINOGRAM', core_dims=(detX, rot),
                             slice_dims=(detY,))
        return data_obj.data.shape

    def __setup_3d_to_4d(self, data_obj, n_angles):
        logging.debug("setting up 4d tomography data from 3d input.")

        data_obj.data = Map3dto4dh5(data_obj.data, n_angles)
        return data_obj.data.get_shape()

    def __setup_4d(self, data_obj):
        logging.debug("setting up 4d tomography data.")
        rot = 0
        detY = 1
        detX = 2
        scan = 3

        data_obj.set_axis_labels('rotation_angle.degrees', 'detector_y.pixel',
                                 'detector_x.pixel', 'scan.number')

        data_obj.add_pattern('PROJECTION', core_dims=(detX, detY),
                             slice_dims=(rot, scan))
        data_obj.add_pattern('SINOGRAM', core_dims=(detX, rot),
                             slice_dims=(detY, scan))
        return data_obj.data.shape

    def __set_dark_and_flat(self, data_obj):
        flat = self.parameters['flat'][0]
        dark = self.parameters['dark'][0]

        if not flat and not dark:
            self.__find_dark_and_flat(data_obj)
        else:
            self.__set_separate_dark_and_flat(data_obj)

    def __find_dark_and_flat(self, data_obj):
        ignore = self.parameters['ignore_flats'] if \
            self.parameters['ignore_flats'] else None
        try:
            image_key = \
                data_obj.backing_file[self.parameters['image_key_path']][...]


            data_obj.data = \
                ImageKey(data_obj, image_key, 0, ignore=ignore)
            #data_obj.set_shape(data_obj.data.get_shape())
        except KeyError:
            cu.user_message("An image key was not found.")
            try:
                data_obj.data = NoImageKey(data_obj, None, 0)
                entry = 'entry1/tomo_entry/instrument/detector/'
                data_obj.data._set_flat_path(entry + 'flatfield')
                data_obj.data._set_dark_path(entry + 'darkfield')
            except KeyError:
                cu.user_message("Dark/flat data was not found in input file.")

    def __set_separate_dark_and_flat(self, data_obj):
        try:
            image_key = \
                data_obj.backing_file[self.parameters['image_key_path']][...]
        except:
            image_key = None
        data_obj.data = NoImageKey(data_obj, image_key, 0)
        self.__set_data(data_obj, 'flat', data_obj.data._set_flat_path)
        self.__set_data(data_obj, 'dark', data_obj.data._set_dark_path)

    def __set_data(self, data_obj, name, func):
        path, entry, scale = self.parameters[name]

        if path.split('/')[0] == 'test_data':
            import os
            path = \
                os.path.dirname(os.path.abspath(__file__))+'/../../../' + path

        ffile = h5py.File(path, 'r')
        try:
            image_key = ffile[self.parameters['image_key_path']][...]
            func(ffile[entry], imagekey=image_key)
        except:
            func(ffile[entry])

        data_obj.data._set_scale(name, scale)

    def __set_rotation_angles(self, data_obj):
        angles = self.parameters['angles']
        if angles is None:
            try:
                entry = 'entry1/tomo_entry/data/rotation_angle'
                angles = data_obj.backing_file[entry][
                    (data_obj.data.get_image_key()) == 0, ...]
            except KeyError:
                logging.warning("No rotation angle entry found in input file.")
                angles = np.linspace(0, 180, data_obj.get_shape()[0])
        else:
            try:
                angles = eval(angles)
            except:
                try:
                    angles = np.loadtxt(angles)
                except:
                    raise Exception('Cannot set angles in loader.')

        data_obj.meta_data.set("rotation_angle", angles)
        return len(angles)

    def __check_angles(self, data_obj, n_angles):
        data_angles = data_obj.data.get_shape()[0]
        if data_angles != n_angles:
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s", n_angles, data_angles)
