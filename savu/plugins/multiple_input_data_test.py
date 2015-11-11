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
.. module:: multiple_input_data_test
   :platform: Unix
   :synopsis: Plugin to test multiple input data sets are passed to process 
   
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class MultipleInputDataTest(Plugin, CpuPlugin):
    """
    The base class from which all plugins should inherit.
    :param in_datasets: Create a list of the dataset(s) to process. Default: [].
    :param out_datasets: Create a list of the dataset(s) to process. Default: [].
    """

    def __init__(self):
        super(MultipleInputDataTest, self).__init__("MultipleInputDataTest")


    def process(self, exp, transport, params):

        in_data = self.get_data_objects(exp.index, "in_data")
        out_data = self.get_data_objects(exp.index, "out_data")
    
        in_data = in_data[0]
        out_data = out_data[0]

        slice_list = in_data.single_slice_list()
        print slice_list
        count = 0
        for sl in slice_list:
            print count
            temp = in_data.data[sl]
            out_data.data[sl] = temp
            count = count + 1
            
        print "plugin complete"

    def setup(self):
        in_datasets, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
#         print in_pData[0].meta_data.get_meta_data('SINOGRAM')# 
        tobecorrected = in_datasets[0]
        monitor = in_datasets[1]
        corrected = out_datasets[0]
        corrected.create_dataset(tobecorrected)
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())
        in_pData[1].plugin_data_setup('SINOGRAM', self.get_max_frames())
        out_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())

#     def setup(self, experiment):
#         """
#         Initial setup of all datasets required as input and output to the 
#         plugin.  This method is called before the process method in the plugin
#         chain.  
#         """
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
#         in_d1.set_current_pattern_name("SINOGRAM")
#         # set frame chunk
#         in_d1.set_nFrames(chunk_size)        
#         # testing fixing a slicing direction
#         # first input parameter is a list of directions to fix (these must be 
#         # defined slice directions)
#         # second input parameter is the index to fix the respective direction to
#         in_d1.set_fixed_directions([0, 1], [0, 0])
# 
#         # get a list of input dataset names required for this plugin
#         in_data_list = self.parameters["in_datasets"]
#         # get all input dataset objects
#         in_d2 = experiment.index["in_data"][in_data_list[1]]
#         # set all input data patterns
#         in_d2.set_current_pattern_name("SINOGRAM")
#         # set frame chunk
#         in_d2.set_nFrames(chunk_size)
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
# 
#         # set pattern for this plugin and the shape
#         out_d1.set_current_pattern_name("SINOGRAM")
#         out_d1.set_shape(in_d1.get_shape())
#         # set frame chunk
#         out_d1.set_nFrames(chunk_size)
# 
#         #----------------------------------------------------------------


    def nInput_datasets(self):
        return 2
         
         
    def nOutput_datasets(self):
        return 1
    
    
    def get_max_frames(self):
        return 8
        
