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


@register_plugin
class PyfaiAzimuthalIntegrator(BaseFilter, CpuPlugin):
    """
    1D azimuthal integrator by pyFAI

    :param use_mask: Should we mask. Default: False.

    """

    def __init__(self):
        logging.debug("Starting 1D azimuthal integrationr")
        super(PyfaiAzimuthalIntegrator,
              self).__init__("PyfaiAzimuthalIntegrator")

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

        sh = in_d1.get_shape()

        if (self.parameters["use_mask"]):
            mask = mData.get_meta_data("mask")
        else:
            mask = np.zeros((sh[-2], sh[-1]))
        # now integrate in radius (1D)
        npts = int(np.round(np.sqrt(sh[-1]**2+sh[-2]**2)))
        self.params = [mask, npts, mData, ai]

    def filter_frames(self, data):
        mData = self.params[2]
        npts = self.params[1]
        mask =self.params[0]
        ai = self.params[3]
        logging.debug("Running azimuthal integration")
        print np.squeeze(data).shape
        print "I'm here"
        fit = ai.xrpd(data=np.squeeze(data), npt=npts)
        mData.set_meta_data('Q', fit[0])
#        mData.set_meta_data('integrated_diffraction_noise',fit[2])
        return fit[1]

    def setup(self):
        print "Hi"
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        shape = in_dataset[0].get_shape()
        # it will always be in Q for this plugin
        # Doesnt this get rid of the other two axes?
        #axis_labels = {in_dataset[0]: '-1.Q.nm^-1'}
        # I just want diffraction data
        in_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        spectra = out_datasets[0]

        # what does this do?
        #remove an axis from all patterns

        # copy all patterns, removing dimension -1 from the core and slice
        # directions, and returning only those that are not empty
        patterns = ['SINOGRAM.-1', 'PROJECTION.-1']
        # stating only 'dimension' will remove the axis label, stating
        # 'dimension.name.unit' name and unit will add or replace it
        axis_labels = ['-1', '-2.name.unit']
        spectra.create_dataset(patterns={in_dataset[0]: patterns},
                               axis_labels={in_dataset[0]: axis_labels},
                               shape={'variable': shape[:-1]})

        spectra.add_pattern("SPECTRUM", core_dir=(-1,),
                            slice_dir=tuple(range(len(shape)-2)))

#        spectra.create_dataset(patterns={in_dataset[0]: ['SPECTRUM']},
#                               axis_labels=axis_labels,
#                               shape={'variable': shape[:-1]})

        # this get the right data in...
        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time
         :returns:  1
        """
        return 1

    def nOutput_datasets(self):
        return 1
#     def setup(self, experiment):
# 
#         chunk_size = self.get_max_frames()
# 
#         #-------------------setup input datasets-------------------------
# 
#         # get a list of input dataset names required for this plugin
#         in_data_list = self.parameters["in_datasets"]
#         # get all input dataset objects
#         in_d1 = experiment.index["in_data"][in_data_list[0]]
#         # set all input data patterns
#         in_d1.set_current_pattern_name("DIFFRACTION") # we take in a pattern
#         # set frame chunk
#         in_d1.set_nFrames(chunk_size)
#         
#         #----------------------------------------------------------------
# 
#         #------------------setup output datasets-------------------------
# 
#         # get a list of output dataset names created by this plugin
#         out_data_list = self.parameters["out_datasets"]
#         
#         # create all out_data objects and associated patterns and meta_data
#         # patterns can be copied, added or both
#         out_d1 = experiment.create_data_object("out_data", out_data_list[0])
#         
#         out_d1.copy_patterns(in_d1.get_patterns())
#         # copy the entire in_data dictionary (image_key, dark and flat will 
#         #be removed since out_data is no longer an instance of TomoRaw)
#         # If you do not want to copy the whole dictionary pass the key word
#         # argument copyKeys = [your list of keys to copy], or alternatively, 
#         # removeKeys = [your list of keys to remove]
#         out_d1.meta_data.copy_dictionary(in_d1.meta_data.get_dictionary(), rawFlag=True)
#         sh = in_d1.get_shape()
#         npts = int(np.round(np.sqrt(sh[-1]**2+sh[-2]**2))) # get the maximum pixel width
#         out_d1.set_shape(sh[:3] + (npts,))# need to figure how to do this properly
#         
#         core_dir = (len(in_d1.get_shape())-2,)
#         
#         out_d1.add_pattern("SPECTRUM", core_dir = core_dir, slice_dir = range(0,core_dir[0],1))
# 
# 
#         # set pattern for this plugin and the shape
#         out_d1.set_current_pattern_name("SPECTRUM")# output a spectrum
# 
#         # set frame chunk
#         out_d1.set_nFrames(chunk_size)
