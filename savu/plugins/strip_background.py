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
.. module:: Background subtraction plugin
   :platform: Unix
   :synopsis: A plugin to automatically strip peaks and subtract background

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""
import logging
from scipy.signal import savgol_filter
import numpy as np
from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
import time
from savu.plugins.utils import register_plugin


@register_plugin
class StripBackground(BaseFilter, CpuPlugin):
    """
    1D background removal. PyMca magic function

    :param iterations: Number of iterations. Default: 100.
    :param window: Half width of the rolling window. Default: 10.
    :param SG_filter_iterations: How many iterations until smoothing occurs. Default: 5.
    :param SG_width: Whats the savitzgy golay window. Default: 35.
    :param SG_polyorder: Whats the savitzgy-golay poly order. Default: 5.

    """

    def __init__(self):
        logging.debug("Stripping background")
        super(StripBackground, self).__init__("StripBackground")

    def filter_frames(self, data):
        data = data[0]
        t1 = time.time()
        its = self.parameters['iterations']
        w = self.parameters['window']
        smoothed = self.parameters['SG_filter_iterations']
        SGwidth = self.parameters['SG_width']
        SGpoly = self.parameters['SG_polyorder']
        print "in the strip_background plugin"
        npts = len(data)
        filtered = savgol_filter(data, SGwidth, SGpoly)
        aved = np.zeros_like(filtered)
        for k in range(its):
            for i in range(npts):
                if (i-w) < 0:
                    aved[i] = (filtered[i] + filtered[i+w])/2.
                elif (i+w) > (len(data)-1):
                    aved[i] = (filtered[i] + filtered[i-w])/2.
                else:
                    aved[i] = (filtered[i-w] + filtered[i] + filtered[i+w])/3.
            filtered[aved < filtered] = aved[aved < filtered]
            if not (k/float(smoothed)-k/int(smoothed)):
                filtered = savgol_filter(filtered, SGwidth, SGpoly)
        t2 = time.time()
        print "Strip iteration took:"+str((t2-t1)*1e3)+"ms"
        return data - filtered

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        stripped = out_datasets[0]
        stripped.create_dataset(in_dataset[0])

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())
        out_pData[0].plugin_data_setup('SPECTRUM', self.get_max_frames())

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1

    def nOutput_datasets(self):
        return 1
