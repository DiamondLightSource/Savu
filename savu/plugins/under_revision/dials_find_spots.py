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
.. module:: dials_find_spots
   :platform: Unix
   :synopsis: A plugin to integrate azimuthally "symmetric" signals i.e. SAXS,\
       WAXS or XRD.Requires a calibration file

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging
import numpy as np
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from scipy.ndimage import gaussian_filter

from dials.array_family import flex
from dials.algorithms.image.threshold import DispersionThreshold


#@register_plugin
class DialsFindSpots(BaseFilter, CpuPlugin):
    """
    finding the single crystal peaks with dials
    :param spotsize: approximate maximum spot size. Default: 45.

    """

    def __init__(self):
        logging.debug("Starting DialsFindSpots")
        super(DialsFindSpots,
              self).__init__("DialsFindSpots")

    def process_frames(self, data):
        data = data[0]
        lp = gaussian_filter(data, 100)
        hp = data - lp # poormans background subtraction
        hp -= np.min(hp)
        sh = hp.shape
        hp = hp.astype('uint32')
        hp = flex.int(hp)
        
        mask = flex.bool(np.ones_like(hp).astype('bool'))
        result1 = flex.bool(np.zeros_like(hp).astype('bool'))
        spots = np.zeros_like(hp).astype('bool')
        
        for i in range(3, self.parameters['spotsize'], 5):
            algorithm = DispersionThreshold(sh, (i, i), 1, 1, 0, -1)
            #print type(hp), type(mask), type(result1)
            thing = algorithm(hp, mask, result1)
            spots = spots + result1.as_numpy_array()
        return [data, spots*data]

    def setup(self):
        in_datasets, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        diffractions = in_datasets[0]
        powder = out_datasets[0]
        single_crystal = out_datasets[1]
        powder.create_dataset(diffractions)
        single_crystal.create_dataset(diffractions)
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        out_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())
        out_pData[1].plugin_data_setup('DIFFRACTION', self.get_max_frames())

    def get_max_frames(self):
        return 'single'

    def nOutput_datasets(self):
        return 2
