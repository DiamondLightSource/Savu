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
import pyFAI

import numpy as np
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


class BaseAzimuthalIntegrator(Plugin, CpuPlugin):
    """
    a base azimuthal integrator for pyfai

    :param use_mask: Should we mask. Default: False.
    :param num_bins: number of bins. Default: 1005.

    """

    def __init__(self, name='BaseAzimuthalIntegrator'):
        logging.debug("Starting 1D azimuthal integrationr")
        super(BaseAzimuthalIntegrator, self).__init__(name)

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
        px_m = mData.get('x_pixel_size')
        bc_m = [mData.get("beam_center_x"),
                mData.get("beam_center_y")]  # in metres
        bc = bc_m / px_m  # convert to pixels
        px = px_m*1e6  # convert to microns
        distance = mData.get('distance')*1e3  # convert to mm
        wl = mData.get('incident_wavelength')[...]  # in m
        self.wl = wl

        yaw = -mData.get("yaw")
        roll = mData.get("roll")

        ai.setFit2D(distance, bc[0], bc[1], yaw, roll, px, px, None)

        ai.set_wavelength(wl)
        logging.debug(ai)

        sh = in_d1.get_shape()

        if (self.parameters["use_mask"]):
            mask = mData.get("mask")
        else:
            mask = np.zeros((sh[-2], sh[-1]))
        # now integrate in radius (1D)print "hello"
        self.npts = self.get_parameters('num_bins')
        self.params = [mask, self.npts, mData, ai]
        # now set the axis values, we shouldn't do this in every slice

        axis, __remapped = \
            ai.integrate1d(data=mask, npt=self.npts, unit='q_A^-1',
                           correctSolidAngle=False)

        self.add_axes_to_meta_data(axis, mData)

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        shape = list(in_dataset[0].get_shape())

        rm_dim = str(in_dataset[0].get_data_patterns()
                     ['SINOGRAM']['slice_dims'][-1])
        patterns = ['SINOGRAM.' + rm_dim, 'PROJECTION.' + rm_dim]

        detX_dim = in_dataset[0].get_data_dimension_by_axis_label('detector_x')
        detY_dim = in_dataset[0].get_data_dimension_by_axis_label('detector_y')
        rm_labels = sorted([detX_dim, detY_dim])[::-1]
        axis_labels = map(str, rm_labels)
        idx = axis_labels.index(str(detY_dim))
        axis_labels[idx] = axis_labels[idx] + '.Q.Angstrom^-1'

        for d in rm_labels:
            del shape[d]
        shape += (self.get_parameters('num_bins'),)

        out_dataset[0].create_dataset(
                patterns={in_dataset[0]: patterns},
                axis_labels=axis_labels,
                shape=tuple(shape))

        spectrum = \
            {'core_dims': (-1,), 'slice_dims': tuple(range(len(shape)-1))}
        out_dataset[0].add_pattern("SPECTRUM", **spectrum)

        in_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        return 'single'

    def nOutput_datasets(self):
        return 1

    def add_axes_to_meta_data(self, axis, mData):
        qanstrom = axis
        dspacing = 2*np.pi/qanstrom
        ttheta = 2*180*np.arcsin(self.wl/(2*dspacing*1e-10))/np.pi
        mData.set('Q', qanstrom)
        mData.set('D', dspacing)
        mData.set('2Theta', ttheta)
