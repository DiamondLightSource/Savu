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
.. module:: i18_xrd_loader
   :platform: Unix
   :synopsis: A class for loading I18's stxm data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.unregistered.i18_loaders.base_i18_multi_modal_loader\
    import BaseI18MultiModalLoader

from savu.data.data_structures.data_types.image_data import ImageData
from savu.plugins.utils import register_plugin
import h5py
import tempfile
import logging
import math
import os
import savu.test.test_utils as tu


class I18XrdLoader(BaseI18MultiModalLoader):
    def __init__(self, name='I18XrdLoader'):
        super(I18XrdLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        data_obj = self.multi_modal_setup('xrd', self.parameters['name'])

        scan_pattern = self.parameters['scan_pattern']
        frame_dim = list(range(len(scan_pattern)))
        shape = []

        for pattern in self.parameters['scan_pattern']:
            if pattern == 'rotation':
                pattern = 'rotation_angle'
            shape.append(len(data_obj.meta_data.get(pattern)))

        path = self.get_path('data_path')
        data_obj.data = ImageData(path, data_obj, frame_dim, shape=tuple(shape))

        # dummy file
        filename = path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        data_obj.set_shape(data_obj.data.get_shape())

        self.set_motors(data_obj, 'xrd')
        self.add_patterns_based_on_acquisition(data_obj, 'xrd')
        self.set_data_reduction_params(data_obj)

        calibrationfile = h5py.File(self.get_path('calibration_path'), 'r')
        # lets just make this all in meters and convert for pyfai in the base integrator
        try:
            logging.debug('testing the version of the calibration file')
            det_str = 'entry1/instrument/detector'
            mData = data_obj.meta_data
            xpix = calibrationfile[det_str + '/detector_module/fast_pixel_direction'][()]*1e-3 # in metres
            mData.set("x_pixel_size",xpix)

            mData.set("beam_center_x",
                    calibrationfile[det_str + '/beam_center_x'][()]*1e-3) #in metres
            mData.set("beam_center_y",
                            calibrationfile[det_str + '/beam_center_y'][()]*1e-3) # in metres
            mData.set("distance",
                            calibrationfile[det_str + '/distance'][()]*1e-3) # in metres
            mData.set("incident_wavelength",
                            calibrationfile['/entry1/calibration_sample/beam'
                                            '/incident_wavelength'][()]*1e-10) # in metres
            mData.set("yaw", -calibrationfile[det_str + '/transformations/euler_b'][()])# in degrees
            mData.set("roll",calibrationfile[det_str + '/transformations/euler_c'][()]-180.0)# in degrees
            logging.debug('.... its the version in DAWN 2.0')
        except KeyError:
            try:
                det_str = 'entry/instrument/detector'
                mData = data_obj.meta_data
                xpix = calibrationfile[det_str + '/x_pixel_size'][()] * 1e-3
                mData.set("x_pixel_size", xpix) # in metres
                mData.set("beam_center_x",
                        calibrationfile[det_str + '/beam_center_x'][()]*xpix)# in metres
                mData.set("beam_center_y",
                                calibrationfile[det_str + '/beam_center_y'][()]*xpix) # in metres
                mData.set("distance",
                                calibrationfile[det_str + '/distance'][()]*1e-3) # in metres
                mData.set("incident_wavelength",
                                calibrationfile['/entry/calibration_sample/beam'
                                                '/incident_wavelength'][()]*1e-10)# in metres
                orien = calibrationfile[det_str + '/detector_orientation'][...].reshape((3, 3))
                yaw = math.degrees(-math.atan2(orien[2, 0], orien[2, 2]))# in degrees
                roll = math.degrees(-math.atan2(orien[0, 1], orien[1, 1]))# in degrees

                mData.set("yaw", -yaw)
                mData.set("roll", roll)
                logging.debug('.... its the legacy version pre-DAWN 2.0')
            except KeyError:
                logging.warning("We don't know what type of calibration file this is")

        self.set_data_reduction_params(data_obj)
        calibrationfile.close()

    def get_path(self,field):
        path = self.parameters[field]
        if path.split(os.sep)[0] == 'Savu':
            path = tu.get_test_data_path(path.split('/test_data/data')[1])
        return path
