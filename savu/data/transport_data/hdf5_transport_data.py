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

import os

from savu.data.transport_data.slice_lists import \
    SliceLists, GlobalData, LocalData
from savu.data.transport_data.base_transport_data import BaseTransportData


class Hdf5TransportData(BaseTransportData, SliceLists):
    """
    The Hdf5TransportData class performs the organising and movement of data.
    """

    def __init__(self, data_obj, name='Hdf5TransportData'):
        super(Hdf5TransportData, self).__init__(data_obj)
        self.mfp = None
        self.params = None
        if os.environ['savu_mode'] == 'basic':
            self.max_frames_function = self._calc_max_frames_transfer_single
        else:
            self.max_frames_function = self._calc_max_frames_transfer_multi

    def _get_slice_lists_per_process(self, dtype):
        pData = self.data._get_plugin_data()
        pData._set_padding_dict()
        self.pad = True if pData.padding else False
        self.transfer_data = GlobalData(dtype, self)
        trans_dict = self.transfer_data._get_dict(pData._plugin.fixed_length)
        proc_dict = LocalData(dtype, self)._get_dict()
        return self.__combine_dicts(trans_dict, proc_dict)

    def __combine_dicts(self, d1, d2):
        for key, value in d2.items():
            d1[key] = value
        return d1

    def _get_padded_data(self, slice_list, end=False):
        return self.transfer_data._get_padded_data(slice_list, end=False)

    def _calc_max_frames_transfer(self, nFrames):
        return self.max_frames_function(nFrames)

