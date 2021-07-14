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
    def __init__(self):
        super(NxxrdLoader, self).__init__("NxxrdLoader")
        # converting lengths to metres
        self.mm = 1e-3
        self.angstrom = 1e-10

    def setup(self):
        self.parameters['in_datasets'] = self.parameters['name']
        path = 'instrument/detector/data'
        data_obj, xrd_entry = \
            self.multi_modal_setup('NXxrd', path, self.parameters['name'])
        mono_energy = data_obj.backing_file[
            xrd_entry.name + '/instrument/monochromator/energy'][()]
        self.exp.meta_data.set("mono_energy", mono_energy)

        self._get_calibration_info(data_obj)
        self._add_diffraction_pattern(data_obj)
        self.set_data_reduction_params(data_obj)

    def _add_diffraction_pattern(self, dObj):
        detX = dObj.get_data_dimension_by_axis_label('detector_x')
        detY = dObj.get_data_dimension_by_axis_label('detector_y')
        cdims = (detX, detY)
        all_dims = list(range(len(dObj.get_shape())))
        sdims = tuple(set(all_dims).difference(cdims))
        dObj.add_pattern("DIFFRACTION", core_dims=cdims, slice_dims=sdims)

    def _get_calibration_info(self, data_obj):
        cfile = h5py.File(self.get_cal_path(), 'r')
        det_str = 'entry/instrument/detector'
        mData = data_obj.meta_data

        try:
            self._set_calibration_new(mData, det_str, cfile)
            logging.debug('.... its the version in DAWN 2.0')
        except KeyError:
            try:
                self._set_calibration_legacy(mData, det_str, cfile)
                logging.debug('.... its the legacy version pre-DAWN 2.0')
            except KeyError:
                emsg = "We don't know what type of calibration file this is"
                logging.warning(emsg)
        cfile.close()

    def _set_calibration_new(self, mData, det_str, cfile):
        xpix_entry = det_str + '/detector_module/fast_pixel_direction'
        xpix = cfile[xpix_entry][()]*self.mm
        mData.set("x_pixel_size", xpix)

        beam_center_x = cfile[det_str + '/beam_center_x'][()]*self.mm
        mData.set("beam_center_x", beam_center_x)

        beam_center_y = cfile[det_str + '/beam_center_y'][()]*self.mm
        mData.set("beam_center_y", beam_center_y)

        distance = cfile[det_str + '/distance'][()]*self.mm
        mData.set("distance", distance)

        wentry = '/entry1/calibration_sample/beam/incident_wavelength'
        wlength = cfile[wentry][()]*self.angstrom
        mData.set("incident_wavelength", wlength)

        yaw = -cfile[det_str + '/transformations/euler_b'][()]
        mData.set("yaw", yaw)

        roll = cfile[det_str + '/transformations/euler_c'][()]-180.0
        mData.set("roll", roll)

    def _set_calibration_legacy(self, mData, det_str, cfile):
        xpix = cfile[det_str + '/x_pixel_size'][()]*self.mm
        mData.set("x_pixel_size", xpix)

        beam_center_x = cfile[det_str + '/beam_center_x'][()]*xpix
        mData.set("beam_center_x", beam_center_x)

        beam_center_y = cfile[det_str + '/beam_center_y'][()]*xpix
        mData.set("beam_center_y", beam_center_y)

        distance = cfile[det_str + '/distance'][()]*self.mm
        mData.set("distance", distance)

        wl_entry = '/entry/calibration_sample/beam/incident_wavelength'
        wavelength = cfile[wl_entry][()]*self.angstrom
        mData.set("incident_wavelength", wavelength)

        orien = cfile[det_str + '/detector_orientation'][...].reshape((3, 3))
        yaw = math.degrees(-math.atan2(orien[2, 0], orien[2, 2]))
        mData.set("yaw", -yaw)

        roll = math.degrees(-math.atan2(orien[0, 1], orien[1, 1]))
        mData.set("roll", roll)

    def get_cal_path(self):
        path = self.parameters['calibration_path']
        if path is None:
            raise Exception("Please add the path to the xrd calibration file.")
        if path.split(os.sep)[0] == 'Savu':
            path = tu.get_test_data_path(path.split('/test_data/data')[1])
        return path
