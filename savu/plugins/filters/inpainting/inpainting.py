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
.. module:: inpainting
   :platform: Unix
   :synopsis: A plugin to inpaint missing data. Data inpainting method from Larix software

.. moduleauthor::Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from larix.methods.misc import INPAINT_LINCOMB

@register_plugin
class Inpainting(Plugin, CpuPlugin):
    """
    A plugin to apply 2D/3D inpainting technique to data. If there is a chunk of
    data missing or one needs to inpaint some data features.

    :u*param mask_range: mask for inpainting is set as a threhsold in a range. Default: [1.0,100].
    :u*param iterations: controls the smoothing level of the inpainted region. Default: 50.
    :u*param windowsize_half: half-size of the smoothing window. Default: 3.
    :u*param sigma: maximum value for the inpainted region. Default: 0.5.
    :u*param pattern: pattern to apply this to. Default: "SINOGRAM".
    """

    def __init__(self):
        super(Inpainting, self).__init__("Inpainting")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        self.mask_range = self.parameters['mask_range']

    def process_frames(self, data):
        input_temp = np.float32(data[0])
        mask = np.zeros(np.shape(input_temp))
        indices = np.where(np.isnan(input_temp))
        input_temp[indices] = 0.0
        mask[(input_temp >= self.mask_range[0]) & (input_temp < self.mask_range[1])] = 1.0
        input_temp = np.ascontiguousarray(input_temp, dtype=np.float32);
        mask = np.ascontiguousarray(mask, dtype=np.uint8);

        pars = {'algorithm' : INPAINT_LINCOMB, \
                'input' : input_temp,\
                'maskData' : mask,
                'number_of_iterations' : self.parameters['iterations'],
                'windowsize_half' : self.parameters['windowsize_half'],
                'sigma' : np.exp(self.parameters['sigma'])}


        (result, mask_upd) = INPAINT_LINCOMB(pars['input'],
                              pars['maskData'],
                              pars['number_of_iterations'],
                              pars['windowsize_half'],
                              pars['sigma'])
        return result

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def get_plugin_pattern(self):
        return self.parameters['pattern']
