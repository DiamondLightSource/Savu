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
.. module:: basic_operations
   :platform: Unix
   :synopsis: Plugin to perform basic mathematical operations on datasets.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class BasicOperations(Plugin, CpuPlugin):

    def __init__(self):
        super(BasicOperations, self).__init__("BasicOperations")

    def pre_process(self):
        self.operations = self._amend_ops(self._set_data_mappings())
        self.out_data = self._set_out_data_names()

    def process_frames(self, data):
        # creates an 'environment' that will store the variables created
        # inside the exec statement
        exec_environment = {'data': data}

        for i in range(len(self.operations)):
            # runs the exec with no builtins, and only 'data' available as a
            #variable initially
            exec(f"{self.out_data[i]} = {self.operations[i]}",
                 {"builtins": None}, exec_environment)

        # Find the result from each exec. Does list comprehension on the
        # results instead of just exec_environment.items to keep the order the
        # same as in out_data
        return [exec_environment[out] for out in self.out_data]

    def setup(self):
        """
        Initial setup of all datasets required as input and output to the \
        plugin.  This method is called before the process method in the \
        plugin chain.
        """

        in_datasets, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        pattern = self.parameters['pattern']

        for pData in in_pData:
            pData.plugin_data_setup(pattern, self.get_max_frames())

        # making the assumption that the basic operations do not change the
        # shape of the data for now.
        copy_datasets = self._get_associated_datasets()
        for i in range(len(out_datasets)):
            out_datasets[i].create_dataset(in_datasets[copy_datasets[i]])
            out_pData[i].plugin_data_setup(pattern, self.get_max_frames())

    def nInput_datasets(self): # needs updating as 'var' is no longer valid
        return 'var'

    def nOutput_datasets(self):
        return 'var'

    def get_max_frames(self):
        return 'multiple'

    def _set_data_mappings(self):
        """
        Maps the input datasets names to the data array passed to process
        frames.
        """
        mapping_dict = {}
        in_datasets = self.get_in_datasets()
        for i in range(len(in_datasets)):
            mapping_dict[in_datasets[i].get_name()] = 'data[' + str(i) + ']'
        return mapping_dict

    def _set_out_data_names(self):
        out_datasets = self.get_out_datasets()
        return [out_datasets[i].get_name() for i in range(len(out_datasets))]

    def _amend_ops(self, mappings_dict):
        """
        Replaces the dataset names in the operations with the data array.
        """
        operations = self.parameters['operations']
        new_ops = []
        for op in operations:
            for key, value in mappings_dict.items():
                op = op.replace(key, value)
            new_ops.append(op)
        return new_ops

    def _get_associated_datasets(self):
        operations = self.parameters['operations']
        in_datasets = self.get_in_datasets()
        data_names = [d.get_name() for d in in_datasets]
        index = []
        for op in operations:
            names = [d for d in data_names if op.find(d) > -1]
            index.append(data_names.index(names[0]))
        return index
