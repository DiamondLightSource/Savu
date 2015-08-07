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
.. module:: plugin
   :platform: Unix
   :synopsis: Base class for all plugins used by Savu

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging
import inspect

from savu.plugins import utils as pu

class Plugin(object):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self, name='Plugin'):
        super(Plugin, self).__init__()
        self.name = name
        self.parameters = {}
        
        
    def setup(self, experiment):
        """
        This method is first to be called after the plugin has been created. 

        :param in_data: The input data object (set to "None" if this is a loader)
        :type in_data: savu.data.experiment
        :param out_data: The output data object
        :type out_data: savu.data.experiment
        """
        logging.error("set_up needs to be implemented for proc %i of %i :" +
                      " input is %s and output is %s", experiment.__class__)
        raise NotImplementedError("setup needs to be implemented")
        

    def populate_default_parameters(self):
        """
        This method should populate all the required parameters with default
        values.  it is used for checking to see if new parameter values are
        appropriate
        
        It makes use of the classes including parameter information in the 
        class docstring such as this 
        :param error_threshold: Convergence threshold. Default: 0.001.
        """
        for clazz in inspect.getmro(self.__class__):
            if clazz != object:
                full_description = pu.find_args(clazz);
                for item in full_description:
                    self.parameters[item['name']] = item['default']

    def set_parameters(self, parameters):
        """
        This method is called after the plugin has been created by the
        pipeline framework

        :param parameters: A dictionary of the parameters for this plugin, or
            None if no customisation is required
        :type parameters: dict
        """
        self.parameters = {}
        self.populate_default_parameters()
        if parameters is not None:
            for key in parameters.keys():
                if key in self.parameters.keys():
                    self.parameters[key] = parameters[key]
                else:
                    raise ValueError("Parameter " + key +
                                     "is not a valid parameter for plugin " +
                                     self.name)
                                     
                                     
    def pre_process(self):
        """
        This method is called after the plugin has been created by the
        pipeline framework as a pre-processing step

        :param parameters: A dictionary of the parameters for this plugin, or
            None if no customisation is required
        :type parameters: dict
        """
        pass

    def post_process(self):
        """
        This method is called after the plugin has been created by the
        pipeline framework as a post-processing step

        :param parameters: A dictionary of the parameters for this plugin, or
            None if no customisation is required
        :type parameters: dict
        """
        pass

    def process(self, data, output, processes, process):
        """
        This method is called after the plugin has been created by the
        pipeline framework and forms the main processing step

        :param data: The input data object.
        :type data: savu.data.structures
        :param data: The output data object
        :type data: savu.data.structures
        :param processes: The number of processes which will be doing the work
        :type path: int
        :param path: The specific process which we are
        :type path: int
        """
        logging.error("process needs to be implemented for proc %i of %i :" +
                      " input is %s and output is %s",
                      process, processes, data.__class__, output.__class__)
        raise NotImplementedError("process needs to be implemented")

    def required_data_type(self):
        """Gets the input data type which is required for the plugin

        :returns:  the class of the data which is expectd

        """
        logging.error("required_data_type needs to be implemented")
        raise NotImplementedError("required_data_type needs to be implemented")

    def output_data_type(self):
        """Gets the output data type which is provided by the plugin

        :returns:  the class of the data which will be provided

        """
        logging.error("output_data_type needs to be implemented")
        raise NotImplementedError("output_data_type needs to be implemented")

    def input_dist(self):
        """Gets the DistArray distribution which is required to create the 
        distributed input array for the plugin

        :returns:  the DistArray distribution of the input to the plugin

        """
        logging.error("input_dist needs to be implemented")
        raise NotImplementedError("input_dist needs to be implemented")

    def output_dist(self):
        """Gets the DistArray distribution which is required to create the 
        distributed output array for the plugin

        :returns:  the DistArray distribution of the output to the plugin

        """
        logging.error("output_dist needs to be implemented")
        raise NotImplementedError("output_dist needs to be implemented")
        
    def get_output_shape(self, input_data):
        """
        Gets the output data shape which is provided by the plugin
        This defaults to the standard size of the data previously generated

        :returns:  the shape of the data which will be output by this plugin

        """
        return None

    def get_citation_information(self):
        """Gets the Citation Information for a plugin

        :returns:  A populated savu.data.plugin_info.CitationInfomration

        """
        return None
