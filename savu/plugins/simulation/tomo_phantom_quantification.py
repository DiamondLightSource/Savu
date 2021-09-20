# Copyright 2020 Diamond Light Source Ltd.
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
.. module:: tomo_phantom_quantification
   :platform: Unix
   :synopsis: A Tomophantom plugin to calculate quantitative values e.g. MSE, RMSE, SSIM

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
import tomophantom
from tomophantom.supp.qualitymetrics import QualityTools

@register_plugin
class TomoPhantomQuantification(Plugin, CpuPlugin):
    def __init__(self):
        super(TomoPhantomQuantification, self).__init__("TomoPhantomQuantification")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        in_pData[1].plugin_data_setup(self.parameters['pattern'], 'single')

        fullData = in_dataset[0]
        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        self.new_shape = (np.prod(np.array(fullData.get_shape())[slice_dirs]), 1)
        out_dataset[0].create_dataset(shape=self.new_shape,
                                      axis_labels=['quantval', 'value'],
                                      remove=True,
                                      transport='hdf5')
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        out_pData[0].plugin_data_setup('METADATA', self.get_max_frames())

    def process_frames(self, data):
        data_temp1 = data[0]
        data_temp2 = data[1]
        indices = np.where(np.isnan(data_temp1))
        data_temp1[indices] = 0.0
        indices = np.where(np.isnan(data_temp2))
        data_temp2[indices] = 0.0

        # collecting values for each slice
        Qtools = QualityTools(data_temp1, data_temp2)
        RMSE = Qtools.rmse()
        print("The Root Mean Square Error is {}".format(RMSE))
        slice_values = [RMSE]
        return np.array([slice_values])

    def nInput_datasets(self):
        return 2
    def nOutput_datasets(self):
        return 1
    def get_max_frames(self):
        return 'single'
