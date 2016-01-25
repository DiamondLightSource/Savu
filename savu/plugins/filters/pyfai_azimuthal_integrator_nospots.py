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
.. module:: radial integration using pyFAI
   :platform: Unix
   :synopsis: A plugin to integrate azimuthally "symmetric" signals i.e. SAXS, WAXS or XRD.Requires a calibration file

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging

import math

import pyFAI

import numpy as np
from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin
import time


@register_plugin
class PyfaiAzimuthalIntegratorNospots(BaseFilter, CpuPlugin):
    """
    1D azimuthal integrator by pyFAI

    :param num_bins: number of bins. Default: 1005.

    """

    def __init__(self):
        logging.debug("Starting 1D azimuthal integrationr")
        super(PyfaiAzimuthalIntegratorNospots,
              self).__init__("PyfaiAzimuthalIntegratorNospots")

    def pre_process(self):
        """
        This method is called after the plugin has been created by the
        pipeline framework as a pre-processing step

        :param parameters: A dictionary of the parameters for this plugin, or
            None if no customisation is required
        :type parameters: dict
        """
        in_dataset, out_datasets = self.get_datasets()
        mData = self.get_in_meta_data()[0]
        in_d1 = in_dataset[0]
        ai = pyFAI.AzimuthalIntegrator()  # get me an integrator object
        ### prep the goemtry
        bc = [mData.get_meta_data("beam_center_x")[...],
              mData.get_meta_data("beam_center_y")[...]]
        distance = mData.get_meta_data('distance')[...]
        wl = mData.get_meta_data('incident_wavelength')[...]
        px = mData.get_meta_data('x_pixel_size')[...]
        orien = mData.get_meta_data(
            'detector_orientation')[...].reshape((3, 3))
        #Transform
        yaw = math.degrees(-math.atan2(orien[2, 0], orien[2, 2]))
        roll = math.degrees(-math.atan2(orien[0, 1], orien[1, 1]))
        ai.setFit2D(distance, bc[0], bc[1], -yaw, roll, px, px, None)
        ai.set_wavelength(wl)
        # now integrate in radius (1D)print "hello"
        self.npts = self.get_parameters('num_bins')
        self.params = [self.npts, mData, ai]

    def filter_frames(self, data):
        t1 = time.time()
        mData = self.params[2]
        mask = data[1]
        mask[mask>0] = 1
        ai = self.params[3]
        logging.debug("Running azimuthal integration")
        fit = ai.xrpd(data=np.squeeze(data[0]), npt=self.npts, mask=mask)
        mData.set_meta_data('Q', fit[0])
#        mData.set_meta_data('integrated_diffraction_noise',fit[2])
        t2 = time.time()
        print "PyFAI iteration took:"+str((t2-t1)*1e3)+"ms"
        return fit[1]

    def post_process(self):
        out_datasets = self.get_out_datasets()
        out_datasets[0].set_variable_array_length(self.npts)

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        shape = in_dataset[0].get_shape()
        # it will always be in Q for this plugin
        # Doesnt this get rid of the other two axes?
        #axis_labels = {in_dataset[0]: '-1.Q.nm^-1'}
        # I just want diffraction data
        in_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        in_pData[1].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        spectra = out_datasets[0]
        num_bins = self.get_parameters('num_bins')
        print num_bins,shape
        print shape[:-2]+(num_bins,)
        # what does this do?
        #remove an axis from all patterns

        # copy all patterns, removing dimension -1 from the core and slice
        # directions, and returning only those that are not empty
        patterns = ['SINOGRAM.-1', 'PROJECTION.-1']
        # stating only 'dimension' will remove the axis label, stating
        # 'dimension.name.unit' name and unit will add or replace it
        axis_labels = ['-1', '-2.name.unit']

#         spectra.create_dataset(patterns={in_dataset[0]: patterns},
#                                axis_labels={in_dataset[0]: axis_labels},
#                                shape={'variable': shape[:-2]})
        print in_dataset
        spectra.create_dataset(patterns={in_dataset[0]: patterns},
                               axis_labels={in_dataset[0]: axis_labels},
                               shape=shape[:-2]+(num_bins,))

        spectrum = {'core_dir': (-1,), 'slice_dir': tuple(range(len(shape)-2))}
        spectra.add_pattern("SPECTRUM", **spectrum)

        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time
         :returns:  1
        """
        return 1

    def nInput_datasets(self):
        return 2