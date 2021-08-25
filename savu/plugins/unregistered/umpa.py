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
.. module:: umpa
   :platform: Unix
   :synopsis: Speckle matching using the UMPA method

.. moduleauthor:: Aaron D. Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
import numpy as np

from speckle_matching import match_speckles
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

#@register_plugin
class Umpa(BaseFilter, CpuPlugin):
    """
    A plugin to perform speckle tracking using the UMPA method
    :param in_datasets: A list of the dataset(s) to process. Default: ['signal','reference'].
    :param out_datasets: A list of the dataset(s) to process. Default: ['T','dx','dy','df','f'].
    :param Nw: 2*Nw + 1 is the width of the window. Default: 4.
    :param step: perform the analysis on every other _step_ pixels in both directions. Default: 1.
    :param max_shift: Do not allow shifts larger than this number of pixels. Default: 4.
    """

    def __init__(self):
        logging.debug("Starting Umpa speckle matching")
        super(Umpa,
              self).__init__("Umpa")

    def process_frames(self, data):
        signals = data[0]
        references = data[1]
        out_dict = match_speckles(signals, references, self.parameters['Nw'], self.parameters['step'], self.parameters['max_shift'], df=True, printout=False)
        return [out_dict['T'],out_dict['dx'],out_dict['dy'],out_dict['df'],out_dict['f']]

    def setup(self):
        # get all in and out datasets required by the plugin
        in_datasets, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        
        ## get the output shape
        Ns = self.parameters['max_shift']
        Nw = self.parameters['Nw']
        step = self.parameters['step']
        inshape = in_datasets[0].get_shape()
        imshape = inshape[-2:]
        restshape = inshape[:-3]
        ROIx = np.arange(Ns+Nw, imshape[0]-Ns-Nw-1, step)
        ROIy = np.arange(Ns+Nw, imshape[1]-Ns-Nw-1, step)


        outshape = restshape + (len(ROIx), len(ROIy))
        allDims = list(range(len(outshape)))
        in_pData[0].plugin_data_setup(self.get_plugin_pattern(), self.get_max_frames())
        in_pData[1].plugin_data_setup(self.get_plugin_pattern(), self.get_max_frames())
        pattern_list = list(in_datasets[0].get_data_patterns().keys())
        pattern_dict = in_datasets[0].get_data_patterns()
        pattern_list.remove(self.get_plugin_pattern())
        proj_in_core_dirs= np.array(in_pData[0].get_core_dimensions())
        first_core_dir = proj_in_core_dirs[0] # should be the scan index
        outlabels = in_datasets[0].get_axis_labels()
        _unused = outlabels.pop(first_core_dir)
        out_datasets[0].create_dataset(axis_labels=outlabels, shape=outshape)
        out_datasets[1].create_dataset(axis_labels=outlabels, shape=outshape)
        out_datasets[2].create_dataset(axis_labels=outlabels, shape=outshape)
        out_datasets[3].create_dataset(axis_labels=outlabels, shape=outshape)
        out_datasets[4].create_dataset(axis_labels=outlabels, shape=outshape)
        
        for pattern in pattern_list:
            core_dir = pattern_dict[pattern]['core_dims']
            core_dir = [ix-1 if ix > first_core_dir else ix for ix in core_dir]
            slice_dir = list(set(allDims)-set(core_dir))
            slice_dir = [ix-1 if ix > first_core_dir else ix for ix in slice_dir]
            dim_info = {'core_dims': core_dir, 'slice_dims': slice_dir}
            
            for dataset in out_datasets:
                dataset.add_pattern(pattern, **dim_info)



        out_pData[0].plugin_data_setup('PROJECTION', self.get_max_frames())
        out_pData[1].plugin_data_setup('PROJECTION', self.get_max_frames())
        out_pData[2].plugin_data_setup('PROJECTION', self.get_max_frames())
        out_pData[3].plugin_data_setup('PROJECTION', self.get_max_frames())
        out_pData[4].plugin_data_setup('PROJECTION', self.get_max_frames())


    def get_plugin_pattern(self):
        return "4D_SCAN"

    def nInput_datasets(self):
        return 2

    def nOutput_datasets(self):
        return 5

    def get_max_frames(self):
        return 1