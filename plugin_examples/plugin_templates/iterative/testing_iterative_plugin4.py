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
.. module:: testing_iterative_plugin4
   :platform: Unix
   :synopsis: Iterative plugin example
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.iterative_plugin import IterativePlugin


@register_plugin
class TestingIterativePlugin4(BaseFilter, IterativePlugin):
    """
    A plugin to test the iterative plugin driver - switching between sinograms
    and projections on each iteration.
    """

    def __init__(self):
        super(TestingIterativePlugin4, self).\
            __init__("TestingIterativePlugin4")

    def pre_process(self):
        self.set_iterations(3)

    def process_frames(self, data):
        return data[0]

    def post_process(self):
        # option here to break out of the iterations
        # self.set_processing_complete()
        pass

    def setup(self):
        # set up the output dataset that is created by the plugin
        in_dataset, out_dataset = self.get_datasets()

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')

        out_dataset[0].create_dataset(in_dataset[0])
        # Clone and set as alternating dataset - should I actually do this here?
        self.clone_dataset(out_dataset[1], out_dataset[0])

        # HOw to set more than one pattern associated with a plugin
        out_pData[0].plugin_data_setup('SINOGRAM', 'single') # set first pattern
        out_pData[1].plugin_data_setup('PROJECTION', 'single') # set first pattern

        # Do I need two plugin data objects?  When should I set this?

        # try replacing input dataset with the output dataset *****option to change the pattern on each iteration?
        # option to set any number of patterns one after another
        self.set_iteration_datasets(0, [in_dataset[0]], [out_dataset[0]], pattern='SINOGRAM')  # Add option for pattern to be a dictionary with different pattern for each dataset
        self.set_iteration_datasets(1, [out_dataset[0]], [out_dataset[1]], pattern='PROJECTION') # PROJECTION
        # out_dataset[0] and out_dataset[1] will continue to alternate for the
        # remaining iterations
        self.set_alternating_patterns(['SINOGRAM', 'PROJECTION']) # or explicitly add it as above or a combination of both
        # it could be that the first two iterations have the same pattern and the remainder alternate
        
        # alternatively to above you could just have
#        self.set_iteration_datasets(0, [in_dataset[0]], [out_dataset[0]])
#        self.set_iteration_datasets(1, [out_dataset[0]], [out_dataset[1]])
#        self.set_alternating_patterns(['SINOGRAM', 'PROJECTION']) # what if there is more than on pattern - this should also be a dictionary
        
        # So, to set different patterns there are two ways
        # first way is to add 'pattern' key word to set_iteration_datasets function call
        # second way is to pass a list of patterns to set_alternating_patterns function call
        # in either case, each entry can be a list of a dictionary
        # if a list apply to all datasets
        # if a dictionary, they should be {dataset: pattern} key value pairs
        
        # Now I just have to make this work - can I just create an extra pluginData object for each dataset and alternate between those?
        # Or will I have to calculate mfp/mft every time?
        # Don't forget to call "finalise_datasets" or whatever the function is (usually called after the setup method)

    def nOutput_datasets(self):
        return 2

    def nClone_datasets(self):
        return 1
