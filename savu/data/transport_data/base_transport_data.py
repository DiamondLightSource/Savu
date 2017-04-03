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
.. module:: base_transport_data
   :platform: Unix
   :synopsis: Base class for transport mechanism data functions.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""


class BaseTransportData(object):
    """
    Implements functions associated with the transport of the data.
    """

    def _get_slice_list_per_process(self, expInfo):
        """
        A slice list required by the current process.
        """
        raise NotImplementedError("get_slice_list_per_process needs to be"
                                  " implemented in  %s", self.__class__)

    def _get_padded_data(self, input_slice_list):
        """
        Fetch the data with relevant padding (as determined by the plugin).
        """
        raise NotImplementedError("get_padded_data needs to be"
                                  " implemented in  %s", self.__class__)
