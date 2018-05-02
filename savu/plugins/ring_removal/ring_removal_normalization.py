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
.. module:: Remove stripe artefacts  
   :platform: Unix
   :synopsis: A plugin working in sinogram space to remove stripe artefacts     
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>    
   
"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
import numpy as np
from scipy.ndimage import gaussian_filter

@register_plugin
class RingRemovalNormalization(Plugin, CpuPlugin):
    """

    Method to remove stripe artefacts in a sinogram (<-> ring artefacts in a reconstructed image)\
    using a normalization-based method with an improvement to reduce the side-effect of creating \
    extra stripes.
    :param radius: Radius of a Gaussian kernel. Default: 5
    :param ratio: In the range of (0.5 -> 1.0). Default: 1.0
    """

    def __init__(self):
        super(RingRemovalNormalization, self).__init__("RingRemovalNormalization")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()
        width_dim = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        height_dim = in_pData[0].get_data_dimension_by_axis_label('rotation_angle')        
        sino_shape = list(in_pData[0].get_shape())
        self.width1 = sino_shape[width_dim]
        self.height1 = sino_shape[height_dim]  
        
    def process_frames(self, data):
        radius = self.parameters['radius']
        ratio = self.parameters['ratio']
        sinogram = np.copy(data[0])
        num_drop = np.int16(1.0 - np.clip(ratio, 0.5, 1.0))
        list_mean = np.mean(np.sort(sinogram, axis=0)[num_drop:self.height1 - num_drop], axis=0)
        list_mean_filtered = gaussian_filter(list_mean, radius)
        list_coef = list_mean_filtered - list_mean
        mat_coef = np.zeros_like(sinogram)
        mat_coef[:] = list_coef        
        sinogram = sinogram + mat_coef            
        return sinogram
