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
.. module:: geo_distance
   :platform: Unix
   :synopsis: Calculate geodesic distance transforms. Wraps the code for calculating geodesic distance transforms, can be a \
   usefull tool for data segmentation with a proper seed initialisation

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

"""
Geodesic transformation of images can be implementated with two approaches: \
fast marching and raster scan. Fast marching is based on the iterative \
propagation of a pixel front with velocity F. Raster scan is based on  \
kernel operations that are sequentially applied over the image in multiple passes.\
In GeoS, the authors proposed to use a 3x3 kernel for forward and \
backward passes for efficient geodesic distance transform, which was used for  \
image segmentation. # https://github.com/taigw/geodesic_distance \
In order to make code work one need to specify valid coordinates to initialise the point\
(seed) from which the distances will be calculated.

lambda: weighting betwween 0.0 and 1.0
          if lambda==0.0, return spatial euclidean distance without considering gradient
          if lambda==1.0, the distance is based on gradient only without using spatial distance
"""
import GeodisTK
import numpy as np

@register_plugin
class GeoDistance(Plugin, CpuPlugin):

    def __init__(self):
        super(GeoDistance, self).__init__("GeoDistance")

    def pre_process(self):
        # extract given parameters
        self.lambda_par = self.parameters['lambda']
        self.iterations = self.parameters['iterations']

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_YZ', 'single')
        in_pData[1].plugin_data_setup('VOLUME_YZ', 'single') # the mask initialisation

        out_dataset[0].create_dataset(in_dataset[0])
        out_pData[0].plugin_data_setup('VOLUME_YZ', 'single')

        fullData = in_dataset[0]
        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        self.new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 1)
        out_dataset[1].create_dataset(shape=self.new_shape,
                                      axis_labels=['max_value', 'angle'],
                                      remove=True,
                                      transport='hdf5')
        out_dataset[1].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[1].plugin_data_setup('METADATA', self.get_max_frames())


    def process_frames(self, data):
        input_temp = data[0]
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0
        if (np.sum(data[1]) > 0):
            geoDist = GeodisTK.geodesic2d_raster_scan(input_temp, data[1], self.lambda_par, self.iterations)
        else:
            geoDist = np.float32(np.zeros(np.shape(data[0])))
        maxvalues = [np.max(geoDist)]
        return [geoDist,np.array([maxvalues])]

    def post_process(self):
        data, max_values = self.get_out_datasets()
        max_stat = np.max(max_values.data[...], axis=0)
        data.meta_data.set(['stats', 'max', 'pattern'], max_stat)

    def nInput_datasets(self):
        return 2
    def nOutput_datasets(self):
        return 2
    def get_max_frames(self):
        return 'single'
