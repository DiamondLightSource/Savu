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
from savu.plugins.filter import Filter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class PyfaiAzimuthalIntegrator(Filter, CpuPlugin):
    """
    1D azimuthal integrator by pyFAI
    
    :param use_mask: Should we mask. Default: False.

    """

    def __init__(self):
        logging.debug("Starting 1D azimuthal integrationr")
        super(PyfaiAzimuthalIntegrator, self).__init__("PyfaiAzimuthalIntegrator")

    def get_filter_padding(self):
        return {}
    
    def get_max_frames(self):
        return 1
    
    def pre_process(self, exp):
        """
        This method is called after the plugin has been created by the
        pipeline framework as a pre-processing step

        :param parameters: A dictionary of the parameters for this plugin, or
            None if no customisation is required
        :type parameters: dict
        """
        in_data_list = self.parameters["in_datasets"]
        in_d1 = exp.index["in_data"][in_data_list[0]]
        mData = in_d1.meta_data # the metadata
        ai = pyFAI.AzimuthalIntegrator()# get me an integrator object
        ### prep the goemtry
        bc = [mData.get_meta_data("beam_center_x")[...], mData.get_meta_data("beam_center_y")[...]]
        distance = mData.get_meta_data('distance')[...]
        wl = mData.get_meta_data('incident_wavelength')[...]
        px = mData.get_meta_data('x_pixel_size')[...]
        orien = mData.get_meta_data('detector_orientation')[...].reshape((3,3))
        #Transform
        yaw = math.degrees(-math.atan2(orien[2,0], orien[2,2]))
        roll = math.degrees(-math.atan2(orien[0,1], orien[1,1]))
        ai.setFit2D(distance, bc[0],bc[1], -yaw, roll, px, px, None)
        ai.set_wavelength(wl)
        
        
        sh = in_d1.get_shape()
        
        if (self.parameters["use_mask"]):
            mask = mData.get_meta_data("mask")
        else:
            mask = np.zeros((sh[-2],sh[-1]))
        # now integrate in radius (1D)
        npts = int(np.round(np.sqrt(sh[-1]**2+sh[-2]**2)))
        params = [mask,npts,mData,ai]
        return params
        
    def filter_frame(self, data, params):
        mData = params[2]
        npts = params[1]
        mask =params[0]
        ai = params[3]
        logging.debug("Running azimuthal integration")
        print np.squeeze(data).shape
        print "I'm here"
        fit=ai.xrpd(data=np.squeeze(data),npt=npts)
        mData.set_meta_data('integrated_diffraction_angle',fit[0])
#        mData.set_meta_data('integrated_diffraction_noise',fit[2])
        return fit[1]
        
    def setup(self, experiment):

        chunk_size = self.get_max_frames()

        #-------------------setup input datasets-------------------------

        # get a list of input dataset names required for this plugin
        in_data_list = self.parameters["in_datasets"]
        # get all input dataset objects
        in_d1 = experiment.index["in_data"][in_data_list[0]]
        # set all input data patterns
        in_d1.set_current_pattern_name("DIFFRACTION") # we take in a pattern
        # set frame chunk
        in_d1.set_nFrames(chunk_size)
        
        #----------------------------------------------------------------

        #------------------setup output datasets-------------------------

        # get a list of output dataset names created by this plugin
        out_data_list = self.parameters["out_datasets"]
        
        # create all out_data objects and associated patterns and meta_data
        # patterns can be copied, added or both
        out_d1 = experiment.create_data_object("out_data", out_data_list[0])
        
        out_d1.copy_patterns(in_d1.get_patterns())
        # copy the entire in_data dictionary (image_key, dark and flat will 
        #be removed since out_data is no longer an instance of TomoRaw)
        # If you do not want to copy the whole dictionary pass the key word
        # argument copyKeys = [your list of keys to copy], or alternatively, 
        # removeKeys = [your list of keys to remove]
        out_d1.meta_data.copy_dictionary(in_d1.meta_data.get_dictionary(), rawFlag=True)
        sh = in_d1.get_shape()
        npts = int(np.round(np.sqrt(sh[-1]**2+sh[-2]**2))) # get the maximum pixel width
        out_d1.set_shape(sh[:3] + (npts,))# need to figure how to do this properly
        
        core_dir = (len(in_d1.get_shape())-2,)
        
        out_d1.add_pattern("SPECTRUM", core_dir = core_dir, slice_dir = range(0,core_dir[0],1))


        # set pattern for this plugin and the shape
        out_d1.set_current_pattern_name("SPECTRUM")# output a spectrum

        # set frame chunk
        out_d1.set_nFrames(chunk_size)
