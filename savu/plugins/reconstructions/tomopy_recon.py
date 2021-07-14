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
.. module:: tomopy_recon
   :platform: Unix
   :synopsis: Wrapper around the tomopy reconstruction algorithms.  See \
       'http://tomopy.readthedocs.io/en/latest/api/tomopy.recon.algorithm.html'

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.driver.cpu_plugin import CpuPlugin

# import tomopy before numpy
import logging
logger = logging.getLogger()
level = logger.getEffectiveLevel()
logger.setLevel(30)
import tomopy
logger.setLevel(level)
import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.reconstructions.base_recon import BaseRecon


@register_plugin
class TomopyRecon(BaseRecon, CpuPlugin):

    def __init__(self):
        super(TomopyRecon, self).__init__("TomopyRecon")

    def pre_process(self):
        self.sl = self.get_plugin_in_datasets()[0].get_slice_dimension()
        vol_shape = self.get_vol_shape()
        filter_name = self.parameters['filter_name']
        # for backwards compatibility
        filter_name = 'none' if filter_name == None else filter_name
        options = {'filter_name': filter_name,
                   'reg_par': self.parameters['reg_par'] - 1,
                   'n_iterations': self.parameters['n_iterations'],
                   'num_gridx': vol_shape[0], 'num_gridy': vol_shape[2]}

        l = vol_shape[0]
        c = np.linspace(-l / 2.0, l / 2.0, l)
        x, y = np.meshgrid(c, c)
        ratio = self.parameters['ratio']
        if isinstance(ratio, list) or isinstance(ratio, tuple):
            self.ratio_mask = ratio[0]
            outer_mask = ratio[1]
            if isinstance(outer_mask, str):
                outer_mask = np.nan
        else:
            self.ratio_mask = ratio
            outer_mask = 0.0

        if isinstance(self.ratio_mask, float):
            r = (l - 1) * self.ratio_mask
            self.manual_mask = \
                np.array((x**2 + y**2 >= (r / 2.0)**2), dtype=np.float)
            self.manual_mask[self.manual_mask == 1] = outer_mask

        self.alg_keys = self.get_allowed_kwargs()
        self.alg = self.parameters['algorithm']
        self.kwargs = {key: options[key] for key in self.alg_keys[self.alg] if
                       key in options.keys()}
        self._finalise_data = self._transpose if self.parameters['outer_pad']\
            else self._apply_mask

    def process_frames(self, data):
        self.sino = data[0]
        self.cors, angles, vol_shape, init = self.get_frame_params()
        if init:
            self.kwargs['init_recon'] = init
        recon = tomopy.recon(self.sino, np.deg2rad(angles),
                             center=self.cors[0], ncore=1, algorithm=self.alg,
                             **self.kwargs)
        return self._finalise_data(recon)

    def _apply_mask(self, recon):
        if isinstance(self.ratio_mask, float):
            recon = tomopy.circ_mask(recon, axis=0, ratio=self.ratio_mask)
            recon = recon + self.manual_mask
        return self._transpose(recon)

    def _transpose(self, recon):
        return np.transpose(recon, (1, 0, 2))

    def get_max_frames(self):
        return 'multiple'

    def get_allowed_kwargs(self):
        return {
            'art': ['num_gridx', 'num_gridy', 'num_iter'],
            'bart': ['num_gridx', 'num_gridy', 'num_iter', 'num_block',
                     'ind_block'],
            'fbp': ['num_gridx', 'num_gridy', 'filter_name', 'filter_par'],
            'gridrec': ['num_gridx', 'num_gridy', 'filter_name', 'filter_par'],
            'mlem': ['num_gridx', 'num_gridy', 'num_iter'],
            'osem': ['num_gridx', 'num_gridy', 'num_iter', 'num_block',
                     'ind_block'],
            'ospml_hybrid': ['num_gridx', 'num_gridy', 'num_iter', 'reg_par',
                             'num_block', 'ind_block'],
            'ospml_quad': ['num_gridx', 'num_gridy', 'num_iter', 'reg_par',
                           'num_block', 'ind_block'],
            'pml_hybrid': ['num_gridx', 'num_gridy', 'num_iter', 'reg_par'],
            'pml_quad': ['num_gridx', 'num_gridy', 'num_iter', 'reg_par'],
            'sirt': ['num_gridx', 'num_gridy', 'num_iter'],
        }
