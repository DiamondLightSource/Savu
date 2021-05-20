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
.. module:: monitor_correction_nd
   :platform: Unix
   :synopsis: A plugin to apply a monitor correction.

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>
"""

import logging
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


#@register_plugin
class MonitorCorrectionNd(BaseFilter, CpuPlugin):

    def __init__(self):
        logging.debug("correcting data")
        super(MonitorCorrectionNd, self).__init__("MonitorCorrectionNd")

    def filter_frames(self, data):
        monitor = data[1]
        to_be_corrected = data[0]
        nom_scale = self.parameters['nominator_scale']
        denom_scale = self.parameters['denominator_scale']
        nom_off = self.parameters['nominator_offset']
        denom_off = self.parameters['denominator_offset']
        monitor = monitor * denom_scale + denom_off
        to_be_corrected = to_be_corrected * nom_scale + nom_off
        out = to_be_corrected / monitor
        return out

    def setup(self):
        in_datasets, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        tobecorrected = in_datasets[0]
        monitor = in_datasets[1]
        corrected = out_datasets[0]
        corrected.create_dataset(tobecorrected)
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(
            self.parameters['data_pattern'], self.get_max_frames())
        in_pData[1].plugin_data_setup(
            self.parameters['monitor_pattern'], self.get_max_frames())
        out_pData[0].plugin_data_setup(
            self.parameters['data_pattern'], self.get_max_frames())   

    def nOutput_datasets(self):
        return 1

    def nInput_datasets(self):
        return 2