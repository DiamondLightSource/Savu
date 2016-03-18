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
.. module:: TransportMechanism
   :platform: Unix
   :synopsis: Class which describes the NXtomo data structure

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""


class TransportData(object):
    """
    Implements functions associated with the transport of the data.
    """

    def load_data(self, start):
        """
        Any data setup required before the plugin chain has started.
        """
        raise NotImplementedError("load_data needs to be implemented in %s",
                                  self.__class__)

    def save_data(self, link_type):
        """
        Any finalisation required of the data after completion.
        """
        raise NotImplementedError("save_data needs to be implemented in %s",
                                  self.__class__)

    def get_slice_list_per_process(self, expInfo):
        """
        A slice list required by the current process.
        """
        raise NotImplementedError("get_slice_list_per_process needs to be"
                                  " implemented in  %s", self.__class__)

    def get_padded_slice_data(self, input_slice_list):
        """
        Fetch the data with relevant padding (as determined by the plugin).
        """
        raise NotImplementedError("get_padded_slice_data needs to be"
                                  " implemented in  %s", self.__class__)

    def get_unpadded_slice_data(self, input_slice_list, padded_dataset):
        """
        Unpad the padded slice data.
        """
        raise NotImplementedError("get_padded_slice_data needs to be"
                                  " implemented in  %s", self.__class__)
