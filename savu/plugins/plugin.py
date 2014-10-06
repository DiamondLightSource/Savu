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


class Plugin(object):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self, name='Plugin'):
        super(Plugin, self).__init__()
        self.name = name
        self.parameters = {}

    def populate_default_parameters(self):
        """
        This method should populate all the required parameters with default
        values.  it is used for checking to see if new parameter values are
        appropriate
        """
        logging.error("populate_default_parameters needs to be implemented")
        raise NotImplementedError("populate_default_parameters " +
                                  "needs to be implemented")

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

    def process(self, data, output, processes, process):
        """
        This method is called after the plugin has been created by the
        pipeline framework

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

    def get_citation_inforamtion(self):
        """Gets the Citation Information for a plugin

        :returns:  A populated savu.data.process_data.CitationInfomration

        """
        return None
