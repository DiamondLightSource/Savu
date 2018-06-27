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
import numpy as np
import itertools

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin

from pmacparser.pmac_parser import PMACParser

@register_plugin
class StageMotion(Plugin, CpuPlugin):
    """
    A Plugin to calculate stage motion from motion positions.
    :u*param a_value: Description of a_value. Default: None.
    :param in_datasets: Create a list of the dataset(s). Default: ["pmin", "pmean", "pmax"].
    :param out_datasets: Create a list of the dataset(s). Default: ["qmin", "qmean", "qmax"].
    """

    NUM_OUTPUT_Q_VARS = 9
    MEAN_INDEX = 1

    def __init__(self):
        super(StageMotion, self).__init__("StageMotion")
        self.parser = None
        self.variables = {}
        self.pvals = None

    def pre_process(self):
        # Get the output shape from the plugin
        out_pdata = self.get_plugin_out_datasets()[0]
        self.out_pshape = out_pdata.get_shape()

        # Get the kinematic program to run and the static variables
        program_from_data = self.get_in_meta_data()[0].get_dictionary()['program']
        variables_from_data = self.get_in_meta_data()[0].get_dictionary()['variables']

        # Create the list of code lines from the kinematic program input
        code_lines = []
        for i in range(len(program_from_data)):
            code_lines.append(str(program_from_data[i]))

        # Set the static variables from the meta input
        for i in range(len(variables_from_data)):
            self.variables[variables_from_data['Name'][i]] = variables_from_data['Value'][i]

        # Create the PMACParser instance
        self.parser = PMACParser(code_lines)

        # Find which dimension of the data passed to process_frames has axis label 'motor'
        p_data = self.get_plugin_in_datasets()[0]
        self.motor_dim = p_data.get_data_dimension_by_axis_label('motor')

        # Fet the axis label values associated with the axis label 'motor'
        data = self.get_in_datasets()[0]
        self.pvals = data.meta_data.get('motor')

    def process_frames(self, data):
        # takes in list of 3 datasets with size (n x m)
        # returns 3 datasets of size (n x m x r)

        data_mean = data[self.MEAN_INDEX]

        # Run the parser on the mean input data to get the mean output data
        self.set_variables_from_data(data_mean)
        output_vars = self.parser.parse(self.variables)

        mean_output = np.zeros(self.out_pshape)
        min_output = np.zeros(self.out_pshape)
        max_output = np.zeros(self.out_pshape)

        # Set the output datasets from the parser output
        for i in range(1, self.NUM_OUTPUT_Q_VARS + 1):
            if 'Q'+str(i) in output_vars:
                mean_output[i-1] = output_vars['Q'+str(i)]
                min_output[i-1] = output_vars['Q'+str(i)]
                max_output[i-1] = output_vars['Q'+str(i)]

        # Dictionary to keep track of the current dataset in use (min, mean, or max) for each pval
        current_pval_index = {}
        for pval in self.pvals:
            current_pval_index[pval] = -1

        # Loop over every combination of min, mean, and max for each pval
        # 0, 1, and 2 here represent min, mean and max index. Getting the product
        # gets us every combination of min, mean and max for each pval
        for j in itertools.product([0, 1, 2], repeat=len(self.pvals)):
            # For each pval, set it to min, mean, or max depending on what iteration we are in
            for index, pval in enumerate(self.pvals):
                new_index = j[index]
                # Only set it if it's changed since last iteration
                if not current_pval_index[pval] == new_index:
                    self.set_variables_from_p_num_data(data[new_index], pval)
                    current_pval_index[pval] = new_index

            # Now run the parser with the current variable values
            parse_result = self.parser.parse(self.variables)

            # Check for and set any minimums or maximums
            for i in range(1, self.NUM_OUTPUT_Q_VARS + 1):
                if 'Q' + str(i) in parse_result:
                    q_result = parse_result['Q' + str(i)]
                    min_output[i - 1] = np.minimum(min_output[i - 1], q_result)
                    max_output[i - 1] = np.maximum(max_output[i - 1], q_result)

        return [min_output, mean_output, max_output]

    def post_process(self):
        pass

    def set_variables_from_data(self, data):
        for index, pval in enumerate(self.pvals):
            self.variables['P' + str(pval)] = data[:, index]

    def set_variables_from_p_num_data(self, data, p_num):
        index = self.pvals.index(p_num)
        self.variables['P' + str(p_num)] = data[:, index]

    def setup(self):
        # take in n x m
        # return n x m x r

        in_datasets, out_datasets = self.get_datasets()
        self.motor_data_dim = \
            in_datasets[0].get_data_dimension_by_axis_label('motor')

        # additional dimension information
        dim_len = self.NUM_OUTPUT_Q_VARS  # = r
        dim_pos = 0
        dim_axis_name = 'Qvalues'
        dim_axis_unit = 'units'

        new_axis = '.'.join(['~' + str(dim_pos), dim_axis_name, dim_axis_unit])
        axis_labels = {in_datasets[0]: [str(self.motor_data_dim), new_axis]}
        self.shape = self.__get_output_shape(in_datasets[0], dim_pos, dim_len)
        pattern = self.__update_pattern_information(in_datasets[0], dim_pos)

        # Populate the output datasets with required information
        out_datasets[0].create_dataset(axis_labels=axis_labels,
                                       shape=self.shape)
        out_datasets[0].add_pattern('MOTOR_POSITION', **pattern)


        out_datasets[1].create_dataset(axis_labels=axis_labels,
                                       shape=self.shape)
        out_datasets[1].add_pattern('MOTOR_POSITION', **pattern)


        out_datasets[2].create_dataset(axis_labels=axis_labels,
                                       shape=self.shape)
        out_datasets[2].add_pattern('MOTOR_POSITION', **pattern)

        # ================== populate plugin datasets ==========================
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('MOTOR_POSITION', 'multiple')
        in_pData[1].plugin_data_setup('MOTOR_POSITION', 'multiple')
        in_pData[2].plugin_data_setup('MOTOR_POSITION', 'multiple')
        out_pData[0].plugin_data_setup('MOTOR_POSITION', 'multiple')
        out_pData[1].plugin_data_setup('MOTOR_POSITION', 'multiple')
        out_pData[2].plugin_data_setup('MOTOR_POSITION', 'multiple')
        # ======================================================================

    def __update_pattern_information(self, dObj, dim_pos):
        pattern = copy.deepcopy(dObj.get_data_patterns()['MOTOR_POSITION'])
        pattern['core_dims'] = (dim_pos,)
        slice_dims = pattern['slice_dims']
        slice_dims = [i if i < dim_pos else i + 1 for i in list(slice_dims)]
        pattern['slice_dims'] = tuple(slice_dims)
        return pattern

    def __get_output_shape(self, dObj, dim_pos, dim_len):
        shape = list(dObj.get_shape())
        del shape[self.motor_data_dim]
        shape.insert(dim_pos, dim_len)
        return tuple(shape)

    def nInput_datasets(self):
        return 3

    def nOutput_datasets(self):
        return 3

