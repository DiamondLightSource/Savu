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


# the information below is used in the auto-API creation for documentation
# and the synopsis appears in the configurator.
"""
.. module:: plugin_template1_with_detailed_notes
   :platform: Unix
   :synopsis: A template to create a simple plugin that takes one dataset as\
   input and returns a similar dataset as output.

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

# this decorator is required for the configurator to recognise the plugin
@register_plugin
class PluginTemplate1WithDetailedNotes(Plugin, CpuPlugin):
# Each class must inherit from the Plugin class and a driver
    def __init__(self):
        super(PluginTemplate1WithDetailedNotes, self).__init__('PluginTemplate1WithDetailedNotes')

    def nInput_datasets(self):
        # Called immediately after the plugin is loaded in to the framework
        return 1

    def nOutput_datasets(self):
        # Called immediately after the plugin is loaded in to the framework
        return 1

    def setup(self):
        # This method is called after the number of in/out datasets associated
        # with the plugin has been established.  It tells the framework all
        # the information it needs to know about the data transport to-and-from
        # the plugin.


        #================== Input and output datasets =========================
        # in_datasets and out_datasets are instances of the Data class.
        # in_datasets were either created in the loader or as output from
        # previous plugins.  out_datasets objects have already been created at
        # this point, but they are empty and need to be populated.

        # Get the Data instances associated with this plugin
        in_dataset, out_dataset = self.get_datasets()

        # see https://savu.readthedocs.io/en/latest/api/savu.data.data_structures.data_create/
        # for more information on creating datasets.

        # Populate the output dataset(s)
        out_dataset[0].create_dataset(in_dataset[0])


        #================== Input and output plugin datasets ==================
        # in_pData and out_pData are instances of the PluginData class.
        # All in_datasets and out_datasets above have an in/out_pData object
        # attached to them temporarily for the duration of the plugin,
        # giving access to additional plugin-specific dataset details. At this
        # point they have been created but not yet populated.

        # Get the PluginData instances attached to the Data instances above
        in_pData, out_pData = self.get_plugin_datasets()

        # Each plugin dataset must call this method and define the data access
        # pattern and number of frames required.
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')

        # 'single', 'multiple' or an int (should only be used if essential)
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')
        
        # All dataset information can be accessed via the Data and PluginData
        # instances

    def pre_process(self):
        # This method is called once before any processing has begun.
        # Access parameters from the doc string in the parameters dictionary
        # e.g. self.parameters['example']
        pass

    def process_frames(self, data):
        # This function is called in a loop by the framework until all the
        # data has been processed.
    
        # Each iteration of the loop will receive a list of numpy arrays
        # (data) containing nInput_datasets with the data sliced as requested
        # in the setup method (SINOGRAM in this case).  If 'multiple' or an 
        # integer number of max_frames are requested the array with have an
        # extra dimension.

        # This plugin has one output dataset, so a single numpy array (a
        # SINOGRAM in this case) should be returned to the framework.
        return data[0]

    def post_process(self):
        # This method is called once after all processing has completed
        # (after an MPI barrier).
        pass