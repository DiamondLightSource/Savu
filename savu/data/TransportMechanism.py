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


class TransportMechanism(object):

    def setup(self, uri):
        raise NotImplementedError("setup needs to be implemented in %s", self.__class__)

    def add_data_block(self, name, shape, dtype):
        raise NotImplementedError("add_data_block needs to be implemented in %s", self.__class__)

    def get_data_block(self, name):
        raise NotImplementedError("get_data_block needs to be implemented in  %s", self.__class__)

    def finalise(self):
        raise NotImplementedError("finalise needs to be implemented in %s", self.__class__)
