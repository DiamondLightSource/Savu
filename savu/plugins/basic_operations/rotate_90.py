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
.. module:: rotate_90
   :platform: Unix
   :synopsis: (Change this) A template to create a simple plugin that takes 
    one dataset as input and returns a similar dataset as output.

.. moduleauthor:: (Change this) Developer Name <email@address.ac.uk>
"""
from copy import deepcopy

from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.core.iterate_plugin_group_utils import enable_iterative_loop, \
    check_if_end_plugin_in_iterate_group, setup_extra_plugin_data_padding

import numpy as np

@register_plugin
class Rotate90(Plugin, CpuPlugin):
# Each class must inherit from the Plugin class and a driver

    def __init__(self):
        super(Rotate90, self).__init__("Rotate90")

    def nInput_datasets(self):
        return 1


    def nOutput_datasets(self):
        return 1


    def setup(self):

        # assumes 3D data and 2D frames

        in_dataset, out_dataset = self.get_datasets()
        pattern = self.parameters["pattern"]
        data_info = in_dataset[0].data_info
        core_dims = data_info["data_patterns"][pattern]["core_dims"]
        c0, c1 = core_dims[0], core_dims[1]                        # core dimensions
        s0 = data_info["data_patterns"][pattern]["slice_dims"][0]  # slice dimension


        # swapping round core dimensions in the shape due to rotation
        new_shape = list(data_info["shape"])
        new_shape[c0], new_shape[c1] = data_info["shape"][c1], data_info["shape"][c0]
        new_shape = tuple(new_shape)

        # swapping round core dimensions in axis labels
        new_axis_labels = deepcopy(data_info["axis_labels"])
        new_axis_labels[c0], new_axis_labels[c1] = data_info["axis_labels"][c1], data_info["axis_labels"][c0]

        # swapping round core dimensions in data patterns
        new_data_patterns = deepcopy(data_info["data_patterns"])
        for pattern in new_data_patterns:
            for dims in new_data_patterns[pattern]:
                dims_list = list(new_data_patterns[pattern][dims])
                for i, dim in enumerate(dims_list):
                    if dim == c0:
                        dims_list[i] = c1
                    elif dim == c1:
                        dims_list[i] = c0
                new_data_patterns[pattern][dims] = tuple(dims_list)

        # creating output dataset with new axis, shape and data patterns to reflect rotated image
        out_dataset[0].create_dataset(shape=new_shape, axis_labels=new_axis_labels)
        out_dataset[0].data_info.set("data_patterns", new_data_patterns)

        in_pData, out_pData = self.get_plugin_datasets()

        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')


    def process_frames(self, data):
        # assumes 2D frame
        if self.parameters["direction"] == "ACW":
            data[0] = np.rot90(data[0], axes=(0, 1))
        elif self.parameters["direction"] == "CW":
            data[0] = np.rot90(data[0], axes=(1, 0))

        return data[0]


    def post_process(self):
        pass

