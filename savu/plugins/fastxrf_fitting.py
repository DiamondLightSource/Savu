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
.. module:: FastXRF fitting
   :platform: Unix
   :synopsis: A plugin to fit XRF spectra quickly

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""
import logging

from flupy.xrf_data_handling.xrf_io import xrfreader
from flupy.xrf_data_handling import XRFDataset
import numpy as np
from savu.plugins.filter import Filter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class FastxrfFitting(Filter, CpuPlugin):
    """
    fast fluorescence fitting with FastXRF. Needs to be on the path
    
    :param sample_attenuators: A dictionary of the attentuators used and their thickness. Default: ''.
    :param detector_distance: sample distance to the detector in mm. Default: 70.
    :param detector_distance: Distance to the detector in mm. Default: 70.
    :param fit_elements: The elements to fit. Default: ['Zn', 'Cu', 'Fe', 'Cr', 'Cl', 'Br', 'Kr'].
    :param exit_angle: Distance to the detector in mm. Default: 70.
    """

    def __init__(self):
        logging.debug("Starting fast fitter")
        super(FastxrfFitting, self).__init__("FastxrfFitting")

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
        datadict = {}
        datadict["rows"] = 1
        datadict["cols"] = 1
        datadict["average_spectrum"] = dataSum
        datadict["Experiment"]={}
        datadict["Experiment"]["incident_energy_keV"] = mData.get_meta_data["mono_energy"]
        datadict["Experiment"]["collection_time"] = 1
        datadict["Detectors"]={}
        datadict["Detectors"]["type"] = dettype
        
        xrfd=XRFDataset()
        xrfd._createSpectraMatrix()
        xrfd.xrfdata(datadict)
        params = [xrfd]
        return params
        
    def filter_frame(self, data, params):
        xrfd = params['xrfd']
        logging.debug("Running azimuthal integration")
        xrfd.fitbatch()
        fit = xrfd.fitdict
        return fit
         
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

        # set pattern for this plugin and the shape
        out_d1.set_current_pattern_name("SPECTRUM")# output a spectrum
        sh = in_d1.get_shape()
        npts = int(np.round(np.sqrt(sh[-1]**2+sh[-2]**2))) # get the maximum pixel width
        out_d1.set_shape(sh[:3] + (npts,))# need to figure how to do this properly
        # set frame chunk
        out_d1.set_nFrames(chunk_size)
