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
.. module:: find_peaks
   :platform: Unix
   :synopsis: A plugin to find the peaks

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.driver.cpu_plugin import CpuPlugin


from savu.plugins.utils import register_plugin
from savu.plugins.filter import Filter
import peakutils as pe
import numpy as np

@register_plugin
class FindPeaks(Filter, CpuPlugin):
    """
    This plugin uses peakutils to find peaks in spectra. This is then added to the metadata.
    :param in_datasets: Create a list of the dataset(s) to process. Default: [].
    :param out_datasets: Create a list of the dataset(s) to process. Default: [].
    :param thresh: Threshold for peak detection Default: 0.03.
    :param min_distance: Minimum distance for peak detection. Default: 15.
    """

    def __init__(self):
        super(FindPeaks, self).__init__("FindPeaks")

    def filter_frame(self, data):
        print "I'm here"
        data = data[0].squeeze()
        PeakIndex = data.meta_data.get_meta_data('PeakIndex')
        PeakIndexNew = pe.indexes(data,thres=self.parameters['thresh'],min_dist=self.parameters['min_distance']).astype(list)
        tmp = [x for x in PeakIndexNew not in PeakIndex]
        PeakIndex.append(tmp)
        PeakIndex = data.meta_data.set_meta_data('PeakIndex',PeakIndex)
        return 0;

    def setup(self, experiment):


        chunk_size = self.get_max_frames()

        #-------------------setup input datasets-------------------------

        # get a list of input dataset names required for this plugin
        in_data_list = self.parameters["in_datasets"]
        # get all input dataset objects
        in_d1 = experiment.index["in_data"][in_data_list[0]]
        # set all input data patterns
        in_d1.set_current_pattern_name("SPECTRUM") # have changed this to work on the first element of the pattern list rather SINOGRAM, since some datasets don't havea singoram adp
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
        out_d1.add_pattern("PROJECTION", core_dir = (0,), slice_dir = (0,)
        out_d1.set_current_pattern_name("1D_METADATA")
        # copy the entire in_data dictionary (image_key, dark and flat will 
        #be removed since out_data is no longer an instance of TomoRaw)
        # If you do not want to copy the whole dictionary pass the key word
        # argument copyKeys = [your list of keys to copy], or alternatively, 
        # removeKeys = [your list of keys to remove]
        out_d1.meta_data.copy_dictionary(in_d1.meta_data.get_dictionary(), rawFlag=True)
        in_d1.meta_data.set_meta_data('PeakIndex',[])
        # set pattern for this plugin and the shape
        out_d1.set_shape((1,))
        # set frame chunk
        out_d1.set_nFrames(chunk_size)


        
    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1
        
