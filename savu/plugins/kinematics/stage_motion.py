# Copyright 2018 Diamond Light Source Ltd.
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
import time
import logging

from typing import Union

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.core.utils import ensure_string

from pmacparser.pmac_parser import PMACParser


@register_plugin
class StageMotion(Plugin, CpuPlugin):
    NUM_OUTPUT_Q_VARS = 9
    MEAN_INDEX = 0
    NUM_DATASETS = 1

    def __init__(self):
        super(StageMotion, self).__init__("StageMotion")
        self.parser = None
        self.variables = {}
        self.pvals = None
        self.num_datasets = self.NUM_DATASETS
        self.use_min_max = False

    def _check_parameters(self):
        use_min_max = self.parameters['use_min_max']
        logging.debug("Config use min max: " + str(use_min_max))
        logging.debug("Experiment meta data use min max: " + \
                          str(self.exp.meta_data.get('use_minmax')))

        # Check the parameters from the config file and the experiment data
        # to check whether to use extra datasets

        # Config value takes priority, check if None
        if self.parameters['use_min_max'] is None:
            # Config was None, so check the value in the experiment data file
            if self.exp.meta_data.get('use_minmax'):
                self.use_min_max = True
        elif self.parameters['use_min_max']:
            self.use_min_max = True

    def pre_process(self):
        # Check the parameters from the config file and the experiment data
        if self.parameters['use_min_max'] is None:
            # Config was None, so check the value in the experiment data file
            if self.exp.meta_data.get('use_minmax'):
                self.use_min_max = True
        elif self.parameters['use_min_max']:
            self.use_min_max = True

        # Get the output shape from the plugin
        out_pdata = self.get_plugin_out_datasets()[0]
        self.out_pshape = out_pdata.get_shape()

        # Get the kinematic program to run and the static variables
        program_from_data = self.get_in_meta_data()[0].get_dictionary()['program']
        variables_from_data = self.get_in_meta_data()[0].get_dictionary()['variables']

        # Create the list of code lines from the kinematic program input
        code_lines = []
        for line in program_from_data:
            code_lines.append(ensure_string(line))

        # Set the static variables from the meta input
        for i in range(len(variables_from_data)):
            name = ensure_string(variables_from_data['Name'][i])
            self.variables[name] = variables_from_data['Value'][i]

        # Create the PMACParser instance
        self.parser = PMACParser(code_lines)

        # Find which dimension of the data passed to process_frames has axis
        # label 'motor'
        p_data = self.get_plugin_in_datasets()[0]
        self.motor_dim = p_data.get_data_dimension_by_axis_label('motor')

        # Fet the axis label values associated with the axis label 'motor'
        data = self.get_in_datasets()[0]
        self.pvals = data.meta_data.get('motor')

    def process_frames(self, data):
        # Data coming in is either an array of 1 or 3 elements
        # If 1 element, then just MEAN data, if 3 then MEAN, MIN, MAX
        # The last dimension represents the P values for each slice
        # Returns either 1 or 3 datasets of size to match the input

        mean_output = np.zeros(self.out_pshape)

        # Check if using all combinations of min, mean and max
        if self.use_min_max:
            # Using min, mean and max
            min_output = np.zeros(self.out_pshape)
            max_output = np.zeros(self.out_pshape)

            num_frames, num_p = np.array(data[0]).shape

            # Create a new data array consisting of all permutations of the P values
            # for min, mean and max, in order to call the parser only once

            # Create an index of the min, mean and max permutations
            index = np.array([list(itertools.product([0, 1, 2], repeat=num_p))])
            index = index.reshape(index.shape[0] * index.shape[1], index.shape[2])

            # Stack and transpose the data array to get it so that the last two dimensions
            # represent the min,mean,max and then the P value
            new_array = np.dstack(np.transpose(data))

            # Create the new data array by slicing the new array with the permutations
            new_data = new_array[:, index, np.arange(num_p)]

            # Now, set the variables to pass to the parser with the new data array
            for index, pval in enumerate(self.pvals):
                self.variables['P' + str(pval)] = new_data[:, :, index]

            # Run the parser
            parse_result = self.parser.parse(self.variables)

            # Extract the Q values from the parse results
            for i in range(1, self.NUM_OUTPUT_Q_VARS + 1):
                if 'Q' + str(i) in parse_result:
                    q_result = parse_result['Q' + str(i)]

                    if not hasattr(q_result, 'size'):
                        size = 1
                    else:
                        size = q_result.size

                    if size > 1:
                        mean_output[i - 1] = q_result[:, self.MEAN_INDEX]
                        max_output[i - 1] = np.amax(q_result, axis=1)
                        min_output[i - 1] = np.amin(q_result, axis=1)
                    else:
                        mean_output[i - 1] = q_result
                        max_output[i - 1] = q_result
                        min_output[i - 1] = q_result

            return [mean_output, min_output, max_output]

        else:
            # Only using mean data
            data_mean = data[self.MEAN_INDEX]

            # Run the parser on the mean input data to get the mean output data
            for index, pval in enumerate(self.pvals):
                self.variables['P' + str(pval)] = data_mean[:, index]

            # Run the parser
            output_vars = self.parser.parse(self.variables)

            # Extract the Q values from the parse results
            for i in range(1, self.NUM_OUTPUT_Q_VARS + 1):
                if 'Q' + str(i) in output_vars:
                    mean_output[i - 1] = output_vars['Q' + str(i)]

            return [mean_output]

    def post_process(self):
        pass

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
        number_of_datasets_in_use = 1
        if self.parameters['use_min_max'] is None:
            # Config was None, so check the value in the experiment data file
            if self.exp.meta_data.get('use_minmax'):
                self.use_min_max = True
        elif self.parameters['use_min_max']:
            self.use_min_max = True
        if self.use_min_max:
            number_of_datasets_in_use = 3

        logging.debug("Number of datasets: " + str(number_of_datasets_in_use))

        for i in range(number_of_datasets_in_use):
            out_datasets[i].create_dataset(axis_labels=axis_labels,
                                           shape=self.shape)
            out_datasets[i].add_pattern('MOTOR_POSITION', **pattern)

        # ================== populate plugin datasets =========================
        in_pData, out_pData = self.get_plugin_datasets()
        for i in range(number_of_datasets_in_use):
            in_pData[i].plugin_data_setup('MOTOR_POSITION', 'multiple')
            out_pData[i].plugin_data_setup('MOTOR_POSITION', 'multiple')
        # =====================================================================

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
        self._check_parameters()
        # If using extra datasets, set them up and increase the number of datasets
        if self.use_min_max:
            logging.debug("Using min and max datasets")
            self.num_datasets += len(self.parameters['extra_in_datasets'])
            self.parameters['in_datasets'].extend(
                    self.parameters['extra_in_datasets'])
        return self.num_datasets

    def nOutput_datasets(self):
        if self.use_min_max:
            self.parameters['out_datasets'].extend(
                    self.parameters['extra_out_datasets'])
        return self.num_datasets
