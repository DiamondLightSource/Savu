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

.. moduleauthor:: Jacob Williamson <scientificsoftware@diamond.ac.uk>
"""
from copy import deepcopy

from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.core.iterate_plugin_group_utils import enable_iterative_loop, \
    check_if_end_plugin_in_iterate_group, setup_extra_plugin_data_padding
from savu.data.data_structures.data_types.data_plus_darks_and_flats \
    import ImageKey

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

        if self.exp.meta_data.get("pre_run"):
            self.stats_obj.calc_stats = False

        in_dataset, out_dataset = self.get_datasets()
        pattern = self.parameters["pattern"]
        data_info = in_dataset[0].data_info
        core_dims = data_info["data_patterns"][pattern]["core_dims"]
        c0, c1 = core_dims[0], core_dims[1]                        # core dimensions
        s0 = data_info["data_patterns"][pattern]["slice_dims"][0]  # slice dimension

        # swapping round core dimensions in the shape due to rotation
        new_shape = list(data_info["shape"])
        new_shape[c0], new_shape[c1] = data_info["shape"][c1], data_info["shape"][c0]
        if self.exp.meta_data.get("pre_run"):
            new_shape[0] = in_dataset[0].data.image_key.shape[0]
        new_shape = tuple(new_shape)

        # swapping round core dimensions in axis labels
        new_axis_labels = deepcopy(data_info["axis_labels"])
        new_axis_labels[c0], new_axis_labels[c1] = data_info["axis_labels"][c1], data_info["axis_labels"][c0]

        # swapping round core dimensions in data patterns
        new_data_patterns = deepcopy(data_info["data_patterns"])
        for pattern in new_data_patterns:
            for dims in new_data_patterns[pattern]:
                if dims != "main_dir":  # not sure what main_dir is ( = slice dim?)
                    dims_list = list(new_data_patterns[pattern][dims])
                    for i, dim in enumerate(dims_list):
                        if dim == c0:
                            dims_list[i] = c1
                        elif dim == c1:
                            dims_list[i] = c0
                    new_data_patterns[pattern][dims] = tuple(dims_list)

        dtype = in_dataset[0].dtype
        if dtype is None:
            dtype = in_dataset[0].data.data.dtype


        # creating output dataset with new axis, shape and data patterns to reflect rotated image
        if dtype:
            out_dataset[0].create_dataset(shape=new_shape, axis_labels=new_axis_labels, dtype=dtype)
        else:
            out_dataset[0].create_dataset(shape=new_shape, axis_labels=new_axis_labels)
        out_dataset[0].data_info.set("data_patterns", new_data_patterns)


        in_pData, out_pData = self.get_plugin_datasets()

        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')


    def pre_process(self):
        if self.exp.meta_data.get("pre_run"):
            in_dataset, out_dataset = self.get_datasets()
            dark = in_dataset[0].data.dark()
            flat = in_dataset[0].data.flat()
            if dark.size:
                in_dataset[0].data.update_dark(self.process_frames_3d(dark))
            if flat.size:
                in_dataset[0].data.update_flat(self.process_frames_3d(flat))
            out_dataset[0].data.image_key = in_dataset[0].data.image_key

    def process_frames(self, data):
        # assumes 2D frame
        if self.parameters["direction"] == "ACW":
            data[0] = np.rot90(data[0], axes=(0, 1))
        elif self.parameters["direction"] == "CW":
            data[0] = np.rot90(data[0], axes=(1, 0))
        return data[0]

    def process_frames_3d(self, data):
        # assumes 3D frame
        if self.parameters["direction"] == "ACW":
            data = np.rot90(data, axes=(1, 2))
        elif self.parameters["direction"] == "CW":
            data = np.rot90(data, axes=(2, 1))
        return data

    def post_process(self):
        if self.exp.meta_data.get("pre_run"):
            in_dataset, out_dataset = self.get_datasets()
            image_key = in_dataset[0].data.image_key

            dark = in_dataset[0].data.dark_updated
            flat = in_dataset[0].data.flat_updated

            file = out_dataset[0].backing_file

            shape = out_dataset[0].data.shape
            dtype = in_dataset[0].data.dtype
            copy_dataset = file.create_dataset("copy", shape=shape, dtype=dtype)
            dataset_name = list(file.keys())[0]

            i_dark = 0
            i_flat = 0
            i_data = 0
            for i, key in enumerate(image_key):
                if int(key) == 2:
                    copy_dataset[i] = dark[i_dark]
                    i_dark += 1
                elif int(key) == 1:
                    copy_dataset[i] = flat[i_flat]
                    i_flat += 1
                elif int(key) == 0:
                    copy_dataset[i] = out_dataset[0].data[i_data]
                    i_data += 1

            file[dataset_name]["data"][::] = file["copy"][::]
            out_dataset[0].data = ImageKey(out_dataset[0], image_key, 0)
            del file["copy"]
