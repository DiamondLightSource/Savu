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
.. module:: stage_motion
   :platform: Unix
   :synopsis: Calculate stage motion from motor positions.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import copy
import logging
import numpy as np

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class StageMotion(Plugin, CpuPlugin):
    """
    A Plugin to calculate stage motion from motion positions.
    :u*param a_value: Description of a_value. Default: None.
    """

    def __init__(self):
        super(StageMotion, self).__init__("StageMotion")

    def pre_process(self):
        data = self.get_in_datasets()[0]
        in_pData = self.get_plugin_in_datasets()[0]
        out_pData = self.get_plugin_out_datasets()[0]
        self.out_pshape = out_pData.get_shape()
        # find which dimension of the data passed to process_frames has \
        # axis label 'motor'
        self.motor_dim = in_pData.get_data_dimension_by_axis_label('motor')
        self.pvals = data.meta_data.get('motor')

    def process_frames(self, data):
        # takes in list of 3 datasets with size (n x m)
        # returns 3 datasets of size (n x m x r)

        # useful to 
        #sl = self.get_current_slice_list()[0][self.slice_dir]
        #current_idx = self.get_global_frame_index()[0][self.count]
        res = np.random.rand(*self.out_pshape)
        return res

    def post_process(self):
        pass

#    def setup(self):
#        # take in n x m
#        # return n x m x r
#
#        in_datasets, out_datasets = self.get_datasets()
#
#        # additional dimension information
#        dim_length = 9  # = r
#        dim_pos = (len(in_datasets[0].get_shape()))
#        dim_axis_name = 'values'
#        dim_axis_unit = 'units'
#
#        new_axis = '.'.join(['~' + str(dim_pos), dim_axis_name, dim_axis_unit])
#        new_shape = in_datasets[0].get_shape() + (dim_length,)
#
#        pattern = self.__update_pattern_information(in_datasets[0], dim_pos)
#
#        # Populate the output datasets with required information
#        for d in out_datasets:
#            d.create_dataset(axis_labels={in_datasets[0]: [new_axis]},
#                             shape=new_shape)
#            d.add_pattern('MOTOR_POSITION', **pattern)
#
#        #================== populate plugin datasets ==========================
#        in_pData, out_pData = self.get_plugin_datasets()
#        for i in range(3):
#            in_pData[i].plugin_data_setup('MOTOR_POSITION', 'single')
#            out_pData[i].plugin_data_setup('MOTOR_POSITION', 'single')
#        #======================================================================
#
#    def __update_pattern_information(self, dObj, dim_pos):
#        # Should this be a new pattern name?
#        pattern = copy.deepcopy(dObj.get_data_patterns()['MOTOR_POSITION'])
#        for key, value in pattern.iteritems():
#            value = [i if i < dim_pos else i+1 for i in list(value)]
#            pattern[key] = tuple(value)
#        pattern['core_dims'] += (dim_pos,)
#        return pattern

    def setup(self):
        # take in n x m
        # return n x m x r

        in_datasets, out_datasets = self.get_datasets()
        self.motor_data_dim = \
            in_datasets[0].get_data_dimension_by_axis_label('motor')

        # additional dimension information
        dim_len = 9  # = r
        dim_pos = 0
        dim_axis_name = 'values'
        dim_axis_unit = 'units'

        new_axis = '.'.join(['~' + str(dim_pos), dim_axis_name, dim_axis_unit])
        axis_labels = {in_datasets[0]: [str(self.motor_data_dim), new_axis]}
        self.shape = self.__get_output_shape(in_datasets[0], dim_pos, dim_len)
        pattern = self.__update_pattern_information(in_datasets[0], dim_pos)

        # Populate the output datasets with required information
        out_datasets[0].create_dataset(axis_labels=axis_labels,
                                       shape=self.shape)
        out_datasets[0].add_pattern('MOTOR_POSITION', **pattern)

        #================== populate plugin datasets ==========================
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('MOTOR_POSITION', 'multiple')
        out_pData[0].plugin_data_setup('MOTOR_POSITION', 'multiple')
        #======================================================================

    def __update_pattern_information(self, dObj, dim_pos):
        pattern = copy.deepcopy(dObj.get_data_patterns()['MOTOR_POSITION'])
        pattern['core_dims'] = (dim_pos,)
        slice_dims = pattern['slice_dims']
        slice_dims = [i if i < dim_pos else i+1 for i in list(slice_dims)]
        pattern['slice_dims'] = tuple(slice_dims)
        return pattern

    def __get_output_shape(self, dObj, dim_pos, dim_len):
        shape = list(dObj.get_shape())
        del shape[self.motor_data_dim]
        shape.insert(dim_pos, dim_len)
        return tuple(shape)

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
