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
from larix.methods.misc import INPAINT_NDF, INPAINT_NM, INPAINT_LINCOMB

@register_plugin
class Inpainting(Plugin, CpuPlugin):
    """
    A plugin to apply 2D/3D inpainting technique to data. If there is a chunk of
    data missing or one needs to inpaint some missing data features.
    """

    def __init__(self):
        super(Inpainting, self).__init__("Inpainting")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        pattern = list(in_dataset[0].get_data_patterns().keys())[0]
        in_pData[0].plugin_data_setup(pattern, 'single')
        out_pData[0].plugin_data_setup(pattern, 'single')
        if self.nInput_datasets() > 1:
            in_pData[1].plugin_data_setup(pattern, 'single')
        self.mask_range = self.parameters['mask_range']

    def process_frames(self, data):
        input_temp = np.float32(data[0]) # get the data in for inpaintng
        if self.nInput_datasets() > 1:
            mask = np.uint8(data[1]) # get the mask if given
        else:
            # build the mask if not given based on threshold values
            mask = np.uint8(np.zeros(np.shape(input_temp)))
            indices = np.where(np.isnan(input_temp))
            input_temp[indices] = 0
            mask[(input_temp >= self.mask_range[0]) & (input_temp < self.mask_range[1])] = 1
        input_temp = np.ascontiguousarray(input_temp, dtype=np.float32)
        mask = np.ascontiguousarray(mask, dtype=np.uint8)

        if self.parameters['method'] == 'LINEARCOMB':
            pars = {'input' : input_temp,
                'maskData' : mask,
                'number_of_iterations' : self.parameters['iterations'],
                'windowsize_half' : self.parameters['windowsize_half'],
                'sigma' : np.exp(self.parameters['sigma'])}

            (result, mask_upd) = INPAINT_LINCOMB(pars['input'],
                              pars['maskData'],
                              pars['number_of_iterations'],
                              pars['windowsize_half'],
                              pars['sigma'])

        elif self.parameters['method'] == 'NONLOCAL_MARCH':
            pars = {'input' : input_temp,
                'maskData' : mask,
                'SW_increment' : self.parameters['search_window_increment'],
                'number_of_iterations' : self.parameters['iterations']}

            (result, mask_upd) = INPAINT_NM(pars['input'],
                                             pars['maskData'],
                                             pars['SW_increment'],
                                             pars['number_of_iterations'])
        elif self.parameters['method'] == 'DIFFUSION':
            pars = {'input': input_temp,
                    'maskData': mask,
                    'regularisation_parameter': self.parameters['regularisation_parameter'], \
                    'edge_parameter': 0,
                    'number_of_iterations': self.parameters['iterations'],
                    'time_marching_parameter': self.parameters['time_marching_parameter'],
                    'penalty_type': 1
                    }
            result = INPAINT_NDF(pars['input'],
                                         pars['maskData'],
                                         pars['regularisation_parameter'],
                                         pars['edge_parameter'],
                                         pars['number_of_iterations'],
                                         pars['time_marching_parameter'],
                                         pars['penalty_type'])
        else:
            print("The inpainting method is not selected!")
        return result

    def nInput_datasets(self):
        return max(len(self.parameters['in_datasets']), 1)

    def nOutput_datasets(self):
        return 1