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
   :synopsis: A class for loading standard tomography data in Nexus format.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import logging
import numpy as np

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin

from savu.data.data_structures.data_types.data_plus_darks_and_flats \
    import ImageKey, NoImageKey


@register_plugin
class NxtomoLoader(BaseLoader):
    """
    """
    def __init__(self, name='NxtomoLoader'):
        super(NxtomoLoader, self).__init__(name)
        self.warnings = []

    def log_warning(self, msg):
        logging.warning(msg)
        self.warnings.append(msg)

    def setup(self):
        exp = self.get_experiment()
        data_obj = exp.create_data_object('in_data', self.parameters['name'])

        data_obj.backing_file = self._get_data_file()

        data_obj.data = self._get_h5_entry(
            data_obj.backing_file, self.parameters['data_path'])

        self._set_dark_and_flat(data_obj)

        self.nFrames = self.__get_nFrames(data_obj)
        if self.nFrames > 1:
            self.__setup_4d(data_obj)
            self.__setup_3d_to_4d(data_obj, self.nFrames)
        else:
            if len(data_obj.data.shape) == 3:
                self._setup_3d(data_obj)
            else:
                self.__setup_4d(data_obj)
            data_obj.set_original_shape(data_obj.data.shape)
        self._set_rotation_angles(data_obj)
        self._set_projection_shifts(data_obj)

        try:
            control = self._get_h5_path(
                data_obj.backing_file, 'entry1/tomo_entry/control/data')
            data_obj.meta_data.set("control", control[...])
        except Exception:
            self.log_warning("No Control information available")

        nAngles = len(data_obj.meta_data.get('rotation_angle'))
        self.__check_angles(data_obj, nAngles)

        self.set_data_reduction_params(data_obj)
        data_obj.data._set_dark_and_flat()

    def _get_h5_entry(self, filename, path):
        if path in filename:
            return filename[path]
        else:
            raise Exception("Path %s not found in %s" % (path, filename))

    def __get_nFrames(self, dObj):
        if self.parameters['3d_to_4d'] is False:
            return 0
        if self.parameters['3d_to_4d'] is True:
            try:
                # for backwards compatibility
                n_frames = eval(self.parameters["angles"], {"builtins": None, "np": np})
                return np.array(n_frames).shape[0]
            except Exception:
                raise Exception("Please specify the angles, or the number of "
                                "frames per scan (via 3d_to_4d param) in the loader.")
        if isinstance(self.parameters['3d_to_4d'], int):
            return self.parameters['3d_to_4d']
        else:
            raise Exception("Unknown value for loader parameter '3d_to_4d', "
                            "please specify an integer value")

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
        data_obj.add_pattern('TANGENTOGRAM', core_dims=(rot, detY),
                             slice_dims=(detX,))

    def __setup_3d_to_4d(self, data_obj, n_frames):
        logging.debug("setting up 4d tomography data from 3d input.")
        from savu.data.data_structures.data_types.map_3dto4d_h5 \
            import Map3dto4dh5

        all_angles = data_obj.data.shape[0]
        if all_angles % n_frames != 0:
            self.log_warning("There are not a complete set of scans in this file, "
                             "loading complete ones only")
        data_obj.data = Map3dto4dh5(data_obj, n_frames)
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
        data_obj.add_pattern('TANGENTOGRAM', core_dims=(rot, detY),
                             slice_dims=(detX, scan))
        data_obj.add_pattern('SINOMOVIE', core_dims=(detX, rot, scan),
                             slice_dims=(detY,))

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
                self.parameters['image_key_path']][...]
            data_obj.data = \
                ImageKey(data_obj, image_key, 0, ignore=ignore)
        except KeyError:
            self.log_warning("An image key was not found.")
            try:
                data_obj.data = NoImageKey(data_obj, None, 0)
                entry = 'entry1/tomo_entry/instrument/detector/'
                data_obj.data._set_flat_path(entry + 'flatfield')
                data_obj.data._set_dark_path(entry + 'darkfield')
            except KeyError:
                self.log_warning("Dark/flat data was not found in input file.")
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
            
        if path.split('/')[0] == 'Savu':
            import os
            savu_base_path = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), '..', '..', '..', '..')
            path = os.path.join(savu_base_path, path.split('Savu')[1][1:])

        ffile = h5py.File(path, 'r')
        try:
            image_key = \
                ffile['entry1/tomo_entry/instrument/detector/image_key'][...]
            func(ffile[entry], imagekey=image_key)
        except:
            func(ffile[entry])

        data_obj.data._set_scale(name, scale)

    def _set_rotation_angles(self, data_obj):
        angles = self.parameters['angles']
        warn_ms = "No angles found so evenly distributing them between 0 and" \
                  " 180 degrees"
        if angles is None:
            angle_key = 'entry1/tomo_entry/data/rotation_angle'
            nxs_angles = self.__get_angles_from_nxs_file(data_obj, angle_key)
            if nxs_angles is None:
                self.log_warning(warn_ms)
                angles = np.linspace(0, 180, data_obj.get_shape()[0])
            else:
                angles = nxs_angles
        else:
            try:
                angles = eval(angles)
            except Exception as e:
                logging.warning(e)
                try:
                    angles = np.loadtxt(angles)
                except Exception as e:
                    logging.debug(e)
                    self.log_warning(warn_ms)
                    angles = np.linspace(0, 180, data_obj.get_shape()[0])
        data_obj.meta_data.set("rotation_angle", angles)
        return len(angles)

    def _set_projection_shifts(self, data_obj):
        proj_shifts = np.zeros((data_obj.get_shape()[0], 2)) # a 2d array of x-y shifts for every projection
        data_obj.meta_data.set("projection_shifts", proj_shifts)
        return len(proj_shifts)

    def __get_angles_from_nxs_file(self, data_obj, path):
        if path in data_obj.backing_file:
            idx = data_obj.data.get_image_key() == 0 if \
                isinstance(data_obj.data, ImageKey) else slice(None)
            return data_obj.backing_file[path][idx]
        else:
            self.log_warning("No rotation angle entry found in input file.")
            return None

    def _get_data_file(self):
        data = self.exp.meta_data.get("data_file")
        return h5py.File(data, 'r')

    def __check_angles(self, data_obj, n_angles):
        rot_dim = data_obj.get_data_dimension_by_axis_label("rotation_angle")
        data_angles = data_obj.data.get_shape()[rot_dim]
        if data_angles != n_angles:
            if self.nFrames > 1:
                rot_angles = data_obj.meta_data.get("rotation_angle")
                try:
                    full_rotations = n_angles // data_angles
                    cleaned_size = full_rotations * data_angles
                    if cleaned_size != n_angles:
                        rot_angles = rot_angles[0:cleaned_size]
                        self.log_warning(
                            "the angle list has more values than expected in it")
                    rot_angles = np.reshape(
                        rot_angles, [full_rotations, data_angles])
                    data_obj.meta_data.set("rotation_angle",
                                           np.transpose(rot_angles))
                    return
                except:
                    pass
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s" % (n_angles, data_angles))

    def executive_summary(self):
        """ Provide a summary to the user for the result of the plugin.

        e.g.
         - Warning, the sample may have shifted during data collection
         - Filter operated normally

        :returns:  A list of string summaries
        """
        if len(self.warnings) == 0:
            return ["Nothing to Report"]
        else:
            return self.warnings
