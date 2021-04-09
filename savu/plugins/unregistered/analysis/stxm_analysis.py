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
.. module:: stxm_analysis
   :platform: Unix
   :synopsis: A plugin to analyse STXM data from area detectors

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

import logging
from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
import numpy as np
from scipy.ndimage import center_of_mass

#@register_plugin
class StxmAnalysis(BaseFilter, CpuPlugin):

    def __init__(self):
        super(StxmAnalysis, self).__init__("StxmAnalysis")

    def pre_process(self):
        if self.parameters['mask_file'] is not None:
            import h5py as h5
            self.mask = h5.File(self.parameters['mask_file'],'r')[self.parameters['mask_path']]
        else:
            self.mask = None
#         print self.mask.shape


    def process_frames(self, data):
        d=data[0]
        d = d*self.mask #  set everything to zero that's in the mask
        bf = np.array([d.sum().sum()])
        df= np.array([d[d<self.parameters['threshold']].sum().sum()])
        dpc_x, dpc_y = center_of_mass(d)
        combined_dpc = np.array([np.sqrt(dpc_x**2 + dpc_y**2)])
        return [bf, df, np.array([dpc_x]), np.array([dpc_y]), combined_dpc]

    def setup(self):
        # set up the output datasets that are created by the plugin
        in_dataset, out_datasets = self.get_datasets()
        shape = in_dataset[0].get_shape()
        new_shape = shape[:-2]+(1,) # we will assume diffraction is the last two slices
        axis_labels = ['-2', '-1.Value.au']
        patterns = ['SINOGRAM.-1', 'PROJECTION.-1', '4D_SCAN.-1']
        bf = out_datasets[0]
        df = out_datasets[1]
        dpc_x = out_datasets[2]
        dpc_y = out_datasets[3]
        combined_dpc = out_datasets[4]
        in_dataset[0].data_info.get_data('axis_labels')
        
        bf.create_dataset(patterns={in_dataset[0]: patterns},
                          axis_labels={in_dataset[0]: axis_labels},
                          shape=new_shape)

        df.create_dataset(patterns={in_dataset[0]: patterns},
                          axis_labels={in_dataset[0]: axis_labels},
                          shape=new_shape)

        dpc_x.create_dataset(patterns={in_dataset[0]: patterns},
                             axis_labels={in_dataset[0]: axis_labels},
                             shape=new_shape)

        dpc_y.create_dataset(patterns={in_dataset[0]: patterns},
                             axis_labels={in_dataset[0]: axis_labels},
                             shape=new_shape)

        combined_dpc.create_dataset(patterns={in_dataset[0]: patterns},
                                    axis_labels={in_dataset[0]: axis_labels},
                                    shape=new_shape)

        channel = {'core_dims': (-1,), 'slice_dims': list(range(len(new_shape)-1))}

        bf.add_pattern("CHANNEL", **channel)
        df.add_pattern("CHANNEL", **channel)
        dpc_x.add_pattern("CHANNEL", **channel)
        dpc_y.add_pattern("CHANNEL", **channel)
        combined_dpc.add_pattern("CHANNEL", **channel)

        # setup plugin datasets
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('DIFFRACTION', self.get_max_frames())

        out_pData[0].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[1].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[2].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[3].plugin_data_setup('CHANNEL', self.get_max_frames())
        out_pData[4].plugin_data_setup('CHANNEL', self.get_max_frames())

    def nOutput_datasets(self):
        return 5

    def get_max_frames(self):
        return 'single'
