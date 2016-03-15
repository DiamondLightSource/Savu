# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: Transport_control
   :platform: Unix
   :synopsis: A TransportControl class which implements functions that control\
   the interaction between the data and plugin layers.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


class TransportControl(object):
    """
    Implements functions that control the interaction between the data and
    plugin layers.
    """

    def _transport_control_setup(self, options):
        """
        Any initial setup required by the transport mechanism, not relating to
        the data.
        """
        raise NotImplementedError("transport_control_setup needs to be "
                                  "implemented in %s", self.__class__)

    def _transport_run_plugin_list(self):
        """
        A loop that contains a call to plugin.run_plugin and anything required
        before or after the execution of a plugin.
        """
        raise NotImplementedError("transport_run_plugin_list needs to be "
                                  "implemented in %s", self.__class__)

    def _process(self, plugin):
        """
        A function to process the plugin, including the passing of data frames.
        """
        raise NotImplementedError("process needs to be implemented in  %s",
                                  self.__class__)
