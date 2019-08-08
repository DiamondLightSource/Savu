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
.. module:: data_crop
   :platform: Unix
   :synopsis: A plugin to crop projection data when the object lies fully within the field of view
.. moduleauthor:: Daniil Kazantsev \
                    <scientificsoftware@diamond.ac.uk>
"""
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin

#import logging
import numpy as np

@register_plugin
class DataCrop(Plugin, CpuPlugin):
    """
    A plugin to crop projection data when the object of interest lies fully within the field of view.

    :param addbox: Add additional pixels to automatically found cropped values . Default: 20.
    :param out_datasets: The default names . Default: ['crop_values'].
    """

    def __init__(self):
        super(DataCrop, self).__init__("DataCrop")

    def pre_process(self):
        self.addbox = np.int(self.parameters['addbox'])

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()
        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())
        self.orig_full_shape = in_dataset[0].get_shape() # includes flats/darks/projections
        #print(self.orig_full_shape)

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

        proj2D[(np.where(proj2D < 0.0))] = 0.0
        nonzeroInd = np.where(proj2D != 0.0) # nonzero data
        zeroInd = np.where(proj2D == 0.0) # zero data
        proj2D[(np.where(proj2D > 1.0))] = 1.0 # make all > 1 equal to one
        proj2D[nonzeroInd] = -np.log(proj2D[nonzeroInd])
        proj2D[zeroInd] = 1e-15 # make it equal to a very small value

        [detectorsHoriz, DetectorVert] = np.shape(proj2D)
        backgr_pix1 = 30 # usually enough to collect noise statistics
        backgr_pix2 = int(2*backgr_pix1) # usually enough to collect noise statistics

        detectorsHoriz_mid = (int)(0.5*detectorsHoriz)
        # extract two small regions which belong to the background
        RegionLEFT = proj2D[0:backgr_pix1,detectorsHoriz_mid-backgr_pix2:detectorsHoriz_mid+backgr_pix2]
        RegionRIGHT = proj2D[-1-backgr_pix1:-1,detectorsHoriz_mid-backgr_pix2:detectorsHoriz_mid+backgr_pix2]
        ValMean = np.mean(RegionLEFT) + np.mean(RegionRIGHT)
        print(proj2D[100,100])

        np.save('proj2D_savu.npy', proj2D)
        # print(ValMean)
        """
        # get 1D mean vectors
        vert_sum = np.mean(proj2D,0)
        horiz_sum = np.mean(proj2D,1)
        # find the maximum values across the vectors
        largest_vert_index = (vert_sum==max(vert_sum)).argmax(axis=0)
        largest_horiz_index = (horiz_sum==max(horiz_sum)).argmax(axis=0)
        # now we need to find the dips of the "gaussian" moving down from the top
        lowest_left_vert_index = (vert_sum[largest_vert_index::-1]<=ValMean).argmax(axis=0)
        lowest_right_vert_index = (vert_sum[largest_vert_index:-1]<=ValMean).argmax(axis=0)
        lowest_left_horz_index = (horiz_sum[largest_horiz_index::-1]<=ValMean).argmax(axis=0)
        lowest_right_horz_index = (horiz_sum[largest_horiz_index:-1]<=ValMean).argmax(axis=0)
        if (lowest_left_vert_index != 0):
            lowest_left_vert_index = largest_vert_index-lowest_left_vert_index
            if ((lowest_left_vert_index-self.addbox) >= 0):
                lowest_left_vert_index -= self.addbox
        if (lowest_right_vert_index != 0):
            lowest_right_vert_index = largest_vert_index+lowest_right_vert_index
            if ((lowest_right_vert_index+self.addbox) < DetectorVert):
                lowest_right_vert_index += self.addbox
        if (lowest_left_horz_index != 0):
            lowest_left_horz_index = largest_horiz_index-lowest_left_horz_index
            if ((lowest_left_horz_index-self.addbox) >= 0):
                lowest_left_horz_index -= self.addbox
        if (lowest_right_horz_index != 0):
            lowest_right_horz_index = largest_horiz_index+lowest_right_horz_index
            if ((lowest_right_horz_index+self.addbox) < detectorsHoriz):
                lowest_right_horz_index += self.addbox

        crop_values = [lowest_left_horz_index,lowest_right_horz_index,lowest_left_vert_index,lowest_right_vert_index]
        """
        crop_values = [0, 0, 0 ,0]
        #print(crop_values)
        return [np.array([crop_values])]

    """
    def post_process(self):
        in_datasets, out_datasets = self.get_datasets()
        crop_values = out_datasets[0].data[...]

        crop_left_horiz = np.min(crop_values[:,0])
        crop_right_horiz = np.max(crop_values[:,1])
        crop_up_vert = np.min(crop_values[:,2])
        crop_down_vert = np.max(crop_values[:,3])

        print("Suggested values for cropping: detectorX from {} to {}, detector Y from {} to {}".format(crop_left_horiz,crop_right_horiz,crop_up_vert,crop_down_vert))
    """

    def nOutput_datasets(self):
        return 1

    def get_max_frames(self):
        return 'single'

    def fix_transport(self):
        return 'hdf5'
