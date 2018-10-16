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
.. module:: min_and_max
   :platform: Unix
   :synopsis: A plugin to calculate the min and max of each frame
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import numpy as np

from savu.plugins.plugin import Plugin
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class MinAndMax(Plugin, CpuPlugin):
    """
    A plugin to calculate the min and max values of each slice (as determined \
    by the pattern parameter)

    :u*param pattern: How to slice the data. Default: 'VOLUME_XZ'.
    :param out_datasets: The default names. Default: ['the_min','the_max'].
    """

    def __init__(self):
        super(MinAndMax, self).__init__("MinAndMax")

    def process_frames(self, data):
        return [np.array([np.min(data[0])]), np.array([np.max(data[0])])]

    def post_process(self):
        # do some curve fitting here
        in_datasets, out_datasets = self.get_datasets()
        the_min = np.squeeze(out_datasets[0].data[...])
        the_max = np.squeeze(out_datasets[1].data[...])
        pattern = self._get_pattern()
        in_datasets[0].meta_data.set(['stats', 'min', pattern], the_min)
        in_datasets[0].meta_data.set(['stats', 'max', pattern], the_max)

    def setup(self):
        in_dataset, out_datasets = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self._get_pattern(), 'single')

        slice_dirs = list(in_dataset[0].get_slice_dimensions())
        orig_shape = in_dataset[0].get_shape()
        new_shape = (np.prod(np.array(orig_shape)[slice_dirs]), 1)

        labels = ['x.pixels', 'y.pixels']
        for i in range(len(out_datasets)):
            out_datasets[i].create_dataset(shape=new_shape, axis_labels=labels,
                        remove=True, transport='hdf5')
            out_datasets[i].add_pattern(
                    "METADATA", core_dims=(1,), slice_dims=(0,))
            out_pData[i].plugin_data_setup('METADATA', 'single')

    def _get_pattern(self):
        return self.parameters['pattern']
        
    def nOutput_datasets(self):
        return 2
