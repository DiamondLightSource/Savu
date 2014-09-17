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

    def __init__(self):
        super(Plugin, self).__init__()

    def process(self, data, processes, process):
        """
        This method is called after the plugin has been created by the
        pipeline framework
        :param data: The input data object.
        :type data: savu.data.structures
        :param processes: The number of processes which will be doing the work
        :type path: int
        :param path: The specific process which we are
        :type path: int
        """
        logging.error("process needs to be implemented for proc %i of %i : %s",
                      process, processes, data.__class__)
        raise NotImplementedError("process needs to be implemented")

    def required_resource(self):
        """Gets the architecture the plugin needs to work

        :returns:  the string CPU or GPU

        """
        logging.error("required_resource needs to be implemented")
        raise NotImplementedError("required_resource needs to be implemented")

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
