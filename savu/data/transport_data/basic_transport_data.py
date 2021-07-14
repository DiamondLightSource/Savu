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
.. module:: hdf5_transport_data
   :platform: Unix
   :synopsis: A data transport class that is inherited by Data class at \
   runtime. It organises the slice list and moves the data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.data.transport_data.slice_lists import LocalData, GlobalData
from savu.data.transport_data.base_transport_data import BaseTransportData


class BasicTransportData(BaseTransportData):
    """
    The Hdf5TransportData class performs the organising and movement of data.
    """

    def __init__(self, data_obj, name='BasicTransportData'):
        super(BasicTransportData, self).__init__(data_obj)

    def _get_slice_lists_per_process(self, dtype):
        pData = self.data._get_plugin_data()
        pData._set_padding_dict()
        self.pad = True if pData.padding else False
        local_dict = LocalData(dtype, self)._get_dict()
        if dtype == 'in':
            gdict = GlobalData(dtype, self)._get_dict()
            local_dict['frames'] = gdict['frames']
            local_dict['current'] = gdict['current']
        return local_dict

    def _calc_max_frames_transfer(self, nFrames):
        t1, t2 = self._calc_max_frames_transfer_single(nFrames)
        return t1, t2

    def _get_padded_data(self, input_slice_list):
        data = self.data.data[input_slice_list]
        return data
