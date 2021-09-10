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
.. module:: dezinger_sinogram_deprecated
   :platform: Unix
   :synopsis: A plugin working in sinogram space to removes zingers. Remove
      zingers (caused by scattered X-rays hitting the CCD chip directly)
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
import numpy as np


class DezingerSinogramDeprecated(Plugin, CpuPlugin):
    """
    """

    def __init__(self):
        super(DezingerSinogramDeprecated, self).__init__("DezingerSinogramDeprecated")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()
        width_dim = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        height_dim = \
            in_pData[0].get_data_dimension_by_axis_label('rotation_angle')
        sino_shape = list(in_pData[0].get_shape())
        self.width1 = sino_shape[width_dim]
        self.height1 = sino_shape[height_dim]

    def process_frames(self, data):
        tolerance = self.parameters['tolerance']
        nhigh = 1.0 + tolerance
        sinogram = np.copy(data[0])
        sinogram[sinogram == 0.0] = np.mean(sinogram)
        sinogram_d = np.roll(sinogram, 1, axis=0)
        sinogram_u = np.roll(sinogram, -1, axis=0)

        list_top = sinogram[0]
        list_top1 = sinogram[1]
        list_top2 = list_top / list_top1
        list_top[list_top2 > nhigh] = list_top1[list_top2 > nhigh]

        list_bottom = sinogram[-1]
        list_bottom1 = sinogram[-2]
        list_bottom2 = list_bottom / list_bottom1
        list_bottom[list_bottom2 > nhigh] = list_bottom1[list_bottom2 > nhigh]

        mat_ratio_d = sinogram / sinogram_d
        sinogram[mat_ratio_d > nhigh] = sinogram_d[mat_ratio_d > nhigh]
        mat_ratio_u = sinogram / sinogram_u
        sinogram[mat_ratio_u > nhigh] = sinogram_u[mat_ratio_u > nhigh]
        sinogram[0] = list_top
        sinogram[-1] = list_bottom
        return sinogram
