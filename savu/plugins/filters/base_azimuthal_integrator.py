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
.. module:: base_azimuthal_integrator
   :platform: Unix
   :synopsis: A plugin to integrate azimuthally "symmetric" signals i.e. \
       SAXS, WAXS or XRD.Requires a calibration file

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging

import math

import pyFAI

import numpy as np
from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from scipy.interpolate import interp1d


class BaseAzimuthalIntegrator(BaseFilter, CpuPlugin):
    """
    a base azimuthal integrator for pyfai

    :param use_mask: Should we mask. Default: False.
    :param num_bins: number of bins. Default: 1005.

    """

    def __init__(self, name):
        logging.debug("Starting 1D azimuthal integrationr")
        super(BaseAzimuthalIntegrator,
              self).__init__(name)

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
        # prep the goemtry
        bc = [mData.get_meta_data("beam_center_x")[...],
              mData.get_meta_data("beam_center_y")[...]]
        distance = mData.get_meta_data('distance')[...]
        wl = mData.get_meta_data('incident_wavelength')[...]*1e-9
        self.wl = wl
        px = mData.get_meta_data('x_pixel_size')[...]*1e3
        orien = mData.get_meta_data(
            'detector_orientation')[...].reshape((3, 3))
        # Transform
        yaw = math.degrees(-math.atan2(orien[2, 0], orien[2, 2]))
        roll = math.degrees(-math.atan2(orien[0, 1], orien[1, 1]))
        ai.setFit2D(distance, bc[0], bc[1], -yaw, roll, px, px, None)
        ai.set_wavelength(wl)

        sh = in_d1.get_shape()

        if (self.parameters["use_mask"]):
            mask = mData.get_meta_data("mask")
        else:
            mask = np.zeros((sh[-2], sh[-1]))
        # now integrate in radius (1D)print "hello"
        self.npts = self.get_parameters('num_bins')
        self.params = [mask, self.npts, mData, ai]

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        shape = in_dataset[0].get_shape()
        # it will always be in Q for this plugin
        # Doesnt this get rid of the other two axes?
        # axis_labels = {in_dataset[0]: '-1.Q.nm^-1'}
        # I just want diffraction data

        in_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        spectra = out_datasets[0]
        num_bins = self.get_parameters('num_bins')
        # what does this do?
        # remove an axis from all patterns

        # copy all patterns, removing dimension -1 from the core and slice
        # directions, and returning only those that are not empty
        patterns = ['SINOGRAM.-1', 'PROJECTION.-1']
        # stating only 'dimension' will remove the axis label, stating
        # 'dimension.name.unit' name and unit will add or replace it

        detY_dim = in_dataset[0].find_axis_label_dimension('detector_y')
        detX_dim = in_dataset[0].find_axis_label_dimension('detector_x')
        if detX_dim < detY_dim:
            detY_dim -= 1
        axis_labels = [str(detX_dim), str(detY_dim) + '.name.unit']

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

    def nOutput_datasets(self):
        return 1

    def add_axes_to_meta_data(self,axis,mData):
        qanstrom = axis # per angstrom, pyfai is wrong
        dspacing = 2*np.pi/qanstrom
        ttheta =  2*180*np.arcsin(self.wl/(2*dspacing*1e-9))/np.pi
        mData.set_meta_data('Q', qanstrom)
        mData.set_meta_data('D', dspacing)
        mData.set_meta_data('2Theta', ttheta)