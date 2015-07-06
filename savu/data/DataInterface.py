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
.. module:: NXtomo
   :platform: Unix
   :synopsis: Class which describes the NXtomo data structure

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""


class DataInterface(object):

    def link_to_file(self, path):
        """
        Populate the Data object with the contents of the file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        raise NotImplementedError("load_from_file needs to be implemented in %s", self.__class__)

    def link_to_transport_mechanism(self, transport):
        """
        Link the data object to some transport mechanism

        """
        raise NotImplementedError("link_to_transport_mechanism needs to be implemented in %s", self.__class__)


    def complete(self):
        """
        finalise

        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        raise NotImplementedError("complete needs to be implemented in %s", self.__class__)