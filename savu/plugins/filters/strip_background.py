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
.. module:: strip_background
   :platform: Unix
   :synopsis: A plugin to automatically strip peaks and subtract background

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""
import logging
from scipy.signal import savgol_filter
import numpy as np
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
import time
from savu.plugins.utils import register_plugin
from copy import deepcopy


@register_plugin
class StripBackground(BaseFilter, CpuPlugin):

    def __init__(self):
        logging.debug("Stripping background")
        super(StripBackground, self).__init__("StripBackground")

    def process_frames(self, data):
        data = data[0]
        t1 = time.time()
        its = self.parameters['iterations']
        w = self.parameters['window']
        smoothed = self.parameters['SG_filter_iterations']
        SGwidth = self.parameters['SG_width']
        SGpoly = self.parameters['SG_polyorder']

        npts = len(data)
        x = np.arange(npts)  # set up some x indices
        filtered = savgol_filter(data, 35, 5) # make the start a bit a bit smoother

        aved = np.zeros_like(filtered)
        bottomedgemain = x < w
        bottomedgerest = (x >= w) & (x < 2*w)

        mainpart = (x >= w) & (x < (npts-w))
        mainpartbottom = (x >= 0) & (x < (npts-2*w))
        mainparttop = (x >= 2*w) & (x < (npts))

        topedgemain = x >= (npts-w)
        topedgerest = (x >= (npts-2*w)) & (x >= (npts-w))

        for k in range(its):
            aved[mainpart] = (filtered[mainpartbottom] + filtered[mainpart] + filtered[mainparttop]) / 3.0
            aved[bottomedgemain] = (filtered[bottomedgemain] + filtered[bottomedgerest]) / 2.0
            aved[topedgemain] = (filtered[topedgemain] + filtered[topedgerest]) / 2.0
            filtered[aved<filtered] = aved[aved<filtered]
            if not (k/float(smoothed)-k/int(smoothed)):
                filtered=savgol_filter(filtered,35,5)

        t2 = time.time()
        logging.debug("Strip iteration took: %s ms", str((t2-t1)*1e3))
        return [data - filtered, filtered]

    def setup(self):
        logging.debug('setting up the background subtraction')
        in_dataset, out_datasets = self.get_datasets()

        in_meta = in_dataset[0].meta_data
        in_dictionary = in_meta.get_dictionary()

        stripped = out_datasets[0]
        stripped.create_dataset(in_dataset[0])
        stripped.meta_data.dict = deepcopy(in_dictionary)

        background = out_datasets[1]
        background.create_dataset(in_dataset[0])
        background.meta_data.dict = deepcopy(in_dictionary)

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[1].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        return 'single'

    def nOutput_datasets(self):
        return 2
