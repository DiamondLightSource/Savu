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
.. module:: i13_txm_nx_loader
   :platform: Unix
   :synopsis: A class for loading I13 TXM data (extension to standard tomography data in Nexus format).

.. moduleauthor:: Malte Storm <malte.storm@diamond.ac.uk>

"""

import h5py
import logging
import numpy as np

import savu.core.utils as cu
from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
from savu.data.data_structures.data_types.data_plus_darks_and_flats \
    import ImageKey, NoImageKey

@register_plugin
class I13TxmNxLoader(BaseLoader):
    """
    A class to load I13 TXM tomography data from a hdf5 file

    :param name: The name assigned to the dataset. Default: 'tomo'.
    :param data_path: Path to the data inside the \
        file. Default: 'entry1/tomo_entry/data/data'.
    :param image_shift: Shifts for each image in a (rot, xy) format. If None, \
        defaults to values in nxs file. Default: None.
    :param image_key_path: Path to the image key entry inside the nxs \
        file. Set this parameter to "None" if use this loader for radiography\
        . Default: 'entry1/tomo_entry/instrument/detector/image_key'.
    :param dark: Optional path to the dark field data file, nxs path and \
        scale value. Default: [None, None, 1].
    :param flat: Optional Path to the flat field data file, nxs path and \
        scale value. Default: [None, None, 1].
    :param angles: A python statement to be evaluated or a file. Default: None.
    :param 3d_to_4d: If this if 4D data stored in 3D then pass an integer \
        value equivalent to the number of projections per 180-degree scan\
        . Default: False.
    :param ignore_flats: List of batch numbers of flats (start at 1) to \
        ignore. Default: None.
    """
    
    def __init__(self, name='I13TxmNxLoader'):
        super(I13TxmNxLoader, self).__init__(name)
        self.warnings = []

    def setup(self):
        exp = self.get_experiment()

        data_obj = exp.create_data_object('in_data', self.parameters['name'])

        data_obj.backing_file = \
            h5py.File(self.exp.meta_data.get("data_file"), 'r')

        data_obj.data = data_obj.backing_file[self.parameters['data_path']]

        self._set_dark_and_flat(data_obj)

        if self.parameters['3d_to_4d']:
            if not self.parameters['angles']:
                raise Exception('Angles are required in the loader.')
            self.__setup_4d(data_obj)
            n_angles = self._set_rotation_angles(data_obj)
            self.__setup_3d_to_4d(data_obj, n_angles)
        else:
            if len(data_obj.data.shape) is 3:
                self._setup_3d(data_obj)
            else:
                self.__setup_4d(data_obj)
            data_obj.set_original_shape(data_obj.data.shape)
            self._set_rotation_angles(data_obj)

        try:
            control = data_obj.backing_file['entry1/tomo_entry/control/data']
            data_obj.meta_data.set("control", control[...])
        except:
            logging.warn("No Control information available")

        nAngles = len(data_obj.meta_data.get('rotation_angle'))
        self.__check_angles(data_obj, nAngles)
        
        self._set_image_shifts(data_obj)
        nShift = len(data_obj.meta_data.get('image_shift'))
        self.__check_angles(data_obj, nShift)

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

    def __setup_3d_to_4d(self, data_obj, n_angles):
        logging.debug("setting up 4d tomography data from 3d input.")
        from savu.data.data_structures.data_types.map_3dto4d_h5 \
            import Map3dto4dh5
        data_obj.data = Map3dto4dh5(data_obj.data, n_angles)
        data_obj.set_original_shape(data_obj.data.get_shape())

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

    def _set_dark_and_flat(self, data_obj):
        flat = self.parameters['flat'][0]
        dark = self.parameters['dark'][0]

        if not flat or not dark:
            self.__find_dark_and_flat(data_obj, flat=flat, dark=dark)
        else:
            self.__set_separate_dark_and_flat(data_obj)

    def __find_dark_and_flat(self, data_obj, flat=None, dark=None):
        ignore = self.parameters['ignore_flats'] if \
            self.parameters['ignore_flats'] else None
        try:
            image_key = data_obj.backing_file[
                'entry1/tomo_entry/instrument/detector/image_key'][...]
            data_obj.data = \
                ImageKey(data_obj, image_key, 0, ignore=ignore)
        except KeyError:
            cu.user_message("An image key was not found.")
            try:
                data_obj.data = NoImageKey(data_obj, None, 0)
                entry = 'entry1/tomo_entry/instrument/detector/'
                data_obj.data._set_flat_path(entry + 'flatfield')
                data_obj.data._set_dark_path(entry + 'darkfield')
            except KeyError:
                cu.user_message("Dark/flat data was not found in input file.")
        data_obj.data._set_dark_and_flat()
        if dark:
            data_obj.data.update_dark(dark)
        if flat:
            data_obj.data.update_flat(flat)

    def __set_separate_dark_and_flat(self, data_obj):
        try:
            image_key = data_obj.backing_file[
                'entry1/tomo_entry/instrument/detector/image_key'][...]
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
                os.path.dirname(os.path.abspath(__file__))+'/../../../../'+path

        ffile = h5py.File(path, 'r')
        try:
            image_key = \
                ffile['entry1/tomo_entry/instrument/detector/image_key'][...]
            func(ffile[entry], imagekey=image_key)
        except:
            func(ffile[entry])

        data_obj.data._set_scale(name, scale)

    def _set_image_shifts(self, data_obj):
        shift = self.parameters['image_shift']
        if shift is None:
            try:
                shift = 'entry1/instrument/image_shift/image_shifts'
                shift = data_obj.backing_file[shift][
                    (data_obj.data.get_image_key()) == 0, ...]
            except KeyError:
                logging.warn("No shift values found in input file.")
                shift = np.zeros((data_obj.get_shape()[0]), 2)
        else:
            try:
                exec("shift = " + shift)
            except:
                try:
                    shift = np.loadtxt(shift)
                except:
                    raise Exception('Cannot set TXM shift in loader.')

        data_obj.meta_data.set("image_shift", shift)
        return len(shift)
    
    def _set_rotation_angles(self, data_obj):
        angles = self.parameters['angles']
        if angles is None:
            try:
                entry = 'entry1/tomo_entry/data/rotation_angle'
                angles = data_obj.backing_file[entry][
                    (data_obj.data.get_image_key()) == 0, ...]
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

        data_obj.meta_data.set("rotation_angle", angles)
        return len(angles)

    def __check_angles(self, data_obj, n_angles):
        data_angles = data_obj.data.get_shape()[0]
        if data_angles != n_angles:
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s", n_angles, data_angles)

