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
.. module:: pyfai_azimuthal_integrator_separate
   :platform: Unix
   :synopsis: A plugin to integrate azimuthally "symmetric" signals \
       i.e. SAXS, WAXS or XRD.Requires a calibration file

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging
from savu.plugins.azimuthal_integrators.base_azimuthal_integrator import \
    BaseAzimuthalIntegrator
from savu.plugins.utils import register_plugin


@register_plugin
class PyfaiAzimuthalIntegratorSeparate(BaseAzimuthalIntegrator):

    def __init__(self):
        logging.debug("Starting 1D azimuthal integrationr")
        super(PyfaiAzimuthalIntegratorSeparate,
              self).__init__("PyfaiAzimuthalIntegratorSeparate")

    def process_frames(self, data):
        logging.debug("Running azimuthal integration")
        mData = self.params[2]
        mask = self.params[0]
        ai = self.params[3]
        num_bins_azim = self.parameters['num_bins_azim']
        num_bins_rad = self.parameters['num_bins']
        percentile = self.parameters['percentile']
        spots, powder = ai.separate(data[0], npt_rad=num_bins_rad, npt_azim=num_bins_azim, percentile=percentile)
        axis, spectra = ai.integrate1d(data=powder,npt=num_bins_rad, unit='q_A^-1')
        return [spectra, spots]

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        shape = in_dataset[0].get_shape()
        # it will always be in Q for this plugin
        # Doesnt this get rid of the other two axes?
        #axis_labels = {in_dataset[0]: '-1.Q.nm^-1'}
        # I just want diffraction data
        in_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        spots = out_datasets[1]
        spectra = out_datasets[0]
        num_bins = self.get_parameters('num_bins')
        # what does this do?
        #remove an axis from all patterns

        # copy all patterns, removing dimension -1 from the core and slice
        # directions, and returning only those that are not empty
        patterns = ['SINOGRAM.-1', 'PROJECTION.-1']
        # stating only 'dimension' will remove the axis label, stating
        # 'dimension.name.unit' name and unit will add or replace it
        axis_labels = ['-1', '-2.name.unit']
        spots.create_dataset(in_dataset[0])
        spectra.create_dataset(patterns={in_dataset[0]: patterns},
                               axis_labels={in_dataset[0]: axis_labels},
                               shape=shape[:-2]+(num_bins,))

        spectrum = \
            {'core_dims': (-1,), 'slice_dims': tuple(range(len(shape)-2))}
        spectra.add_pattern("SPECTRUM", **spectrum)

        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[1].plugin_data_setup('DIFFRACTION', self.get_max_frames())

    def nOutput_datasets(self):
        return 2
