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
.. module:: dosna_transport_data
   :platform: Unix
   :synopsis: A data transport class that is inherited by Data class at \
   runtime. It organises the slice list and moves the data.

.. moduleauthor:: Emilio Perez Juarez <scientificsoftware@diamond.ac.uk>

"""

from savu.data.transport_data.hdf5_transport_data import Hdf5TransportData


class DosnaTransportData(Hdf5TransportData):
    """
    The DosnaTransportData class performs the organising and movement of data.
    """

    def __init__(self, data_obj, name='DosnaTransportData'):
        super(DosnaTransportData, self).__init__(data_obj)
