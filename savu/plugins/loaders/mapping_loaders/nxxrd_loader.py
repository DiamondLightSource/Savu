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
.. module:: nxxrd_loader
   :platform: Unix
   :synopsis: A class for loading nxxrd data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os.path as os
import h5py
import logging
import math
from savu.plugins.loaders.mapping_loaders.base_multi_modal_loader \
    import BaseMultiModalLoader
from savu.plugins.utils import register_plugin
import savu.test.test_utils as tu


@register_plugin
class NxxrdLoader(BaseMultiModalLoader):
    """
    A class to load tomography data from an NXxrd file

    :param calibration_path: path to the calibration file. Default: None.
    """

    def __init__(self):
        super(NxxrdLoader, self).__init__("NxxrdLoader")

    def setup(self):
        data_str = '/instrument/detector/data'
        data_obj, xrd_entry = self.multi_modal_setup('NXxrd', data_str)
        mono_energy = data_obj.backing_file[
            xrd_entry.name + '/instrument/monochromator/energy'].value
        self.exp.meta_data.set("mono_energy", mono_energy)
        self.set_motors(data_obj, xrd_entry, 'xrd')


        self.add_patterns_based_on_acquisition(data_obj, 'xrd')

        calibrationfile = h5py.File(self.get_cal_path(), 'r')
        try:
            logging.debug('testing the version of the calibration file')
            det_str = 'entry1/instrument/detector'
            mData = data_obj.meta_data
            xpix = calibrationfile[det_str + '/detector_module/fast_pixel_direction'].value*1e-3 # in metres

            mData.set("x_pixel_size",xpix)

            mData.set("beam_center_x",
                    calibrationfile[det_str + '/beam_center_x'].value*1e-3) #in metres 
            mData.set("beam_center_y",
                            calibrationfile[det_str + '/beam_center_y'].value*1e-3) # in metres
            mData.set("distance",
                            calibrationfile[det_str + '/distance'].value*1e-3) # in metres
            mData.set("incident_wavelength",
                            calibrationfile['/entry1/calibration_sample/beam'
                                            '/incident_wavelength'].value*1e-10) # in metres
            mData.set("yaw", -calibrationfile[det_str + '/transformations/euler_b'].value)# in degrees
            mData.set("roll",calibrationfile[det_str + '/transformations/euler_c'].value-180.0)# in degrees
            logging.debug('.... its the version in DAWN 2.0')
        except KeyError:
            try:
                det_str = 'entry/instrument/detector'
                mData = data_obj.meta_data
                xpix = calibrationfile[det_str + '/x_pixel_size'].value * 1e-3
                mData.set("x_pixel_size", xpix) # in metres
                mData.set("beam_center_x",
                        calibrationfile[det_str + '/beam_center_x'].value*xpix)# in metres
                mData.set("beam_center_y",
                                calibrationfile[det_str + '/beam_center_y'].value*xpix) # in metres
                mData.set("distance",
                                calibrationfile[det_str + '/distance'].value*1e-3) # in metres
                mData.set("incident_wavelength",
                                calibrationfile['/entry/calibration_sample/beam'
                                                '/incident_wavelength'].value*1e-10)# in metres
                orien = calibrationfile[det_str + '/detector_orientation'][...].reshape((3, 3))
                yaw = math.degrees(-math.atan2(orien[2, 0], orien[2, 2]))# in degrees
                roll = math.degrees(-math.atan2(orien[0, 1], orien[1, 1]))# in degrees
                
                mData.set("yaw", -yaw)
                mData.set("roll", roll)
                logging.debug('.... its the legacy version pre-DAWN 2.0')
            except KeyError:
                logging.warn("We don't know what type of calibration file this is")


        self.set_data_reduction_params(data_obj)
        calibrationfile.close()

    def get_cal_path(self):
        path = self.parameters['calibration_path']
        if path.split(os.sep)[0] == 'Savu':
            path = tu.get_test_data_path(path.split('/test_data/data')[1])
        return path
