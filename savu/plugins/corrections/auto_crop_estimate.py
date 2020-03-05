# Copyright 2019 Diamond Light Source Ltd.
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
.. module:: auto_crop_estimate
   :platform: Unix
   :synopsis: A plugin to estimate cropping values in order to crop projections automatically
.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin

# add larix autocropping module
from larix.methods.misc import AUTOCROP

#import logging
import numpy as np

@register_plugin
class AutoCropEstimate(Plugin, CpuPlugin):
    """
    A plugin to estimate cropping values (indices) in order to crop projection data automatically \
    (works well when the object of interest lies fully within the field of view). This plugin will return a \
    metadata dataset indices2crop with estimated cropping indices to be accessed later wih plugin auto_crop_projections.
    
    :param threshold: A threshold to control the cropping strength . Default: 0.1.
    :param margin_skip: Skip number of pixels around the image border . Default: 10.    
    :param statbox_size: The size of the box to collect background statistics (mean) . Default: 30.
    :param increase_crop: Increase crop values to ensure more accurate cropping . Default: 40.
    :param method: A method how final indices across multiple frames are estimated,\
    choose minmax, mean or median . Default: 'median'.
    :param out_datasets: 4xN(frames) array with indices to crop . Default: ['indices2crop'].
    """

    def __init__(self):
        super(AutoCropEstimate, self).__init__("AutoCropEstimate")

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())
        self.orig_full_shape = in_dataset[0].get_shape() # includes flats/darks/projections

        fullData = in_dataset[0]
        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        self.new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 4)

        out_dataset[0].create_dataset(shape=self.new_shape ,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True,
                                      transport='hdf5')
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())

    def process_frames(self, data):        
        proj2D = data[0] # get 2D projection image [DetectorHoriz, DetectorVert]        
        proj2D[proj2D > 0.0] = -np.log(proj2D[proj2D > 0.0])
        proj2D[proj2D < 0.0] = 0.0
        
        pars = {'input_data' : proj2D, 			   # input grayscale image
        	'threshold' : self.parameters['threshold'], # threshold to control cropping strength
	        'margin_skip' : self.parameters['margin_skip'], # skip number of pixels around the image border
        	'statbox_size' : self.parameters['statbox_size'],# the size of the box to collect background statistics (mean)
	        'increase_crop' : self.parameters['increase_crop']} # increase crop values to ensure better cropping

        indices2crop = AUTOCROP(pars['input_data'], pars['threshold'],
                           pars['margin_skip'], pars['statbox_size'],
                           pars['increase_crop'])

        #print(indices2crop)
        return [np.array([indices2crop])]

    def post_process(self):
        in_datasets, out_datasets = self.get_datasets()
        cropped_indices = out_datasets[0].data[...]
        
        if (str(self.parameters['method']) == 'minmax'):
            crop_left_horiz = np.min(cropped_indices[:,0])
            crop_right_horiz = np.max(cropped_indices[:,1])
            crop_up_vert = np.min(cropped_indices[:,2])
            crop_down_vert = np.max(cropped_indices[:,3])                 
        elif (str(self.parameters['method']) == 'mean'):
            crop_left_horiz = np.mean(cropped_indices[:,0])
            crop_right_horiz = np.mean(cropped_indices[:,1])
            crop_up_vert = np.mean(cropped_indices[:,2])
            crop_down_vert = np.mean(cropped_indices[:,3])
        elif (str(self.parameters['method']) == 'median'):
            crop_left_horiz = np.median(cropped_indices[:,0])
            crop_right_horiz = np.median(cropped_indices[:,1])
            crop_up_vert = np.median(cropped_indices[:,2])
            crop_down_vert = np.median(cropped_indices[:,3])     
        else:
            print("Please select a method how final indices across multiple frames are estimated, choose minmax, mean or median")           
            
        #print("Suggested values for cropping: detectorHoriz from {} to {}, detectorVertical from {} to {}".format(crop_left_horiz,crop_right_horiz,crop_up_vert,crop_down_vert))
        in_datasets[0].meta_data.set('indices2crop', [crop_left_horiz, crop_right_horiz, crop_up_vert, crop_down_vert])
        #print(in_datasets[0].get_name())       
        # a possible option to incorporate values into 
        #preview = [:, mid, :]
        #self.preview_flag = self.set_preview(in_datasets[0], preview)

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'
