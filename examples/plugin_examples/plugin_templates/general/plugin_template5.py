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
.. module:: plugin_template5
   :platform: Unix
   :synopsis: A template to create a plugin with a single input dataset and \
   multiple output datasets, that do not resemble the input dataset and are \
   not retained by the framework.

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""
import numpy as np

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class PluginTemplate5(Plugin, CpuPlugin):

    def __init__(self):
        super(PluginTemplate5, self).__init__('PluginTemplate5')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 2

    def setup(self):

        in_dataset, out_dataset = self.get_datasets()

        # get the full shape of the data before previewing
        full_shape = in_dataset[0].get_shape()

        # reduce the data as per data_subset parameter
        self.set_preview(in_dataset[0], self.parameters['preview'])

        # get the reduced shape of the data after previewing
        reduced_shape = in_dataset[0].get_shape()

        slice_dirs = np.array(in_dataset[0].get_slice_dimensions())
        new_shape = (np.prod(np.array(reduced_shape)[slice_dirs]), 1)
        full_length = (np.prod(np.array(full_shape)[slice_dirs]), 1)

        #=================== populate output datasets =========================
        # the output datasets are of a different type (i.e different shape,
        # axis labels and patterns)  to the input dataset, so more information
        # is required.

        # the first output dataset contains one value for each...
        out_dataset[0].create_dataset(shape=new_shape,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True,
                                      transport='hdf5')
        # currently there are no patterns assigned to this dataset - add one.
        out_dataset[0].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))

        # write something here about this being a dummy dataset...
        out_dataset[1].create_dataset(shape=full_length,
                                      axis_labels=['x.pixels', 'y.pixels'],
                                      remove=True,
                                      transport='hdf5')
        # currently there are no patterns assigned to this dataset - add one.
        out_dataset[1].add_pattern("METADATA", core_dims=(1,), slice_dims=(0,))
        #======================================================================

        #================== populate plugin datasets ==========================
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())
        out_pData[0].plugin_data_setup('METADATA', 'single')
        out_pData[1].plugin_data_setup('METADATA', 'single')
        #======================================================================

    def pre_process(self):
        pass

    def process_frames(self, data):
        pass

    def post_process(self):
        # Add some information to post process *** how are these datasets
        # processed
        pass
