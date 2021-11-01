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
.. module:: iterative_ccpi_denoising
   :platform: Unix
   :synopsis: Iterative plugin example
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.iterative_plugin import IterativePlugin


@register_plugin
class IterativeCcpiDenoising(BaseFilter, IterativePlugin):
    """
    A plugin to test the iterative plugin driver
    
    :u*param nIterations: Number of iterations.  Default: 10.

    """

    def __init__(self):
        super(IterativeCcpiDenoising, self).__init__("IterativeCcpiDenoising")

    def pre_process(self):
        self.set_iterations(self.parameters['plugin_iterations'])

    def process_frames(self, data):
        # A random example function
        if self.get_iteration() == 0:
            return np.zeros(data[0].shape, dtype=np.float32)
        return data[1] + np.ones(data[0].shape, dtype=np.float32)*10

    def post_process(self):
        # option here to break out of the iterations
        #self.set_processing_complete()
        pass

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')

        # Cloned datasets are at the end of the out_dataset list
        out_dataset[0].create_dataset(in_dataset[0])

        # What is a cloned dataset?
        # Since each dataset in Savu has its own backing hdf5 file, a dataset
        # cannot be used for input and output at the same time.  So, in the
        # case of iterative plugins, if a dataset is used as output and then
        # as input on the next iteration, the subsequent output must be a
        # different file.
        # A cloned dataset is a copy of another dataset but with a different
        # backing file.  It doesn't have a name, is not accessible as a dataset
        # in the framework and is only used in alternation with another
        # dataset to allow it to be used as both input and output
        # simultaneously.
        
        # This is a cloned dataset (of out_dataset[0])
        self.create_clone(out_dataset[1], out_dataset[0])

        out_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[1].plugin_data_setup('SINOGRAM', 'single')

        # input and output datasets for the first iteration
        self.set_iteration_datasets(0, [in_dataset[0]], [out_dataset[0]])
        # input and output datasets for subsequent iterations
        self.set_iteration_datasets(1, [in_dataset[0], out_dataset[0]],
                                    [out_dataset[1]])
        # out_dataset[0] and out_dataset[1] will continue to alternate for
        # all remaining iterations i.e. output becomes input and input becomes
        # output.

    # total number of output datasets
    def nOutput_datasets(self):
        return 2

    # total number of output datasets that are clones
    def nClone_datasets(self):
        return 1
