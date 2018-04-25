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
        pass

    def process_frames(self, data):
        # takes in list of 3 datasets with size (n x m)
        # returns 3 datasets of size (n x m x r)
        print len(data)
        shape = data[0].shape + (9,)
        res = np.random.rand(*shape)
        return [res, res, res]

    def post_process(self):
        pass

    def setup(self):
        # take in n x m
        # return n x m x r

        in_datasets, out_datasets = self.get_datasets()

        # additional dimension information
        dim_length = 9  # = r
        dim_pos = (len(in_datasets[0].get_shape()))
        dim_axis_name = 'values'
        dim_axis_unit = 'units'

        new_axis = '.'.join(['~' + str(dim_pos), dim_axis_name, dim_axis_unit])
        new_shape = in_datasets[0].get_shape() + (dim_length,)

        pattern = self.__update_pattern_information(in_datasets[0], dim_pos)

        # Populate the output datasets with required information
        for d in out_datasets:
            d.create_dataset(axis_labels={in_datasets[0]: [new_axis]},
                             shape=new_shape)
            d.add_pattern('MOTOR_POSITION', **pattern)

        #================== populate plugin datasets ==========================
        in_pData, out_pData = self.get_plugin_datasets()
        for i in range(3):
            in_pData[i].plugin_data_setup('MOTOR_POSITION', 'single')
            out_pData[i].plugin_data_setup('MOTOR_POSITION', 'single')
        #======================================================================

    def __update_pattern_information(self, dObj, dim_pos):
        # Should this be a new pattern name?
        pattern = copy.deepcopy(dObj.get_data_patterns()['MOTOR_POSITION'])
        for key, value in pattern.iteritems():
            value = [i if i < dim_pos else i+1 for i in list(value)]
            pattern[key] = tuple(value)
        pattern['core_dims'] += (dim_pos,)
        return pattern

    def nInput_datasets(self):
        return 3

    def nOutput_datasets(self):
        return 3
