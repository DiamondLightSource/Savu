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
.. module:: plugin_name_example
   :platform: Unix
   :synopsis: (Change this) A template to create a simple plugin that takes 
    one dataset as input and returns a similar dataset as output.

.. moduleauthor:: (Change this) Developer Name <email@address.ac.uk>
"""
from savu.plugins.utils import register_plugin
from savu.plugins.plugin import Plugin
# Import any additional libraries or base plugins here.

# This decorator is required for the configurator to recognise the plugin
@register_plugin
class PluginNameExample(Plugin):
# Each class must inherit from the Plugin class and a driver

    def __init__(self):
        super(PluginNameExample, self).__init__("PluginNameExample")

    def pre_process(self):
        """ This method is called immediately after base_pre_process(). """
        pass  

    def process_frames(self, data):
        """
        This method is called after the plugin has been created by the
        pipeline framework and forms the main processing step

        :param data: A list of numpy arrays for each input dataset.
        :type data: list(np.array)
        """
        pass

    def post_process(self):
        """
        This method is called after the process function in the pipeline
        framework as a post-processing step. All processes will have finished
        performing the main processing at this stage.

        :param exp: An experiment object, holding input and output datasets
        :type exp: experiment class instance
        """
        pass

    def setup(self):
        """
        Initial setup of all datasets required as input and output to the
        plugin.  This method is called before the process method in the plugin
        chain.
        """
        in_dataset, out_dataset = self.get_datasets()
  