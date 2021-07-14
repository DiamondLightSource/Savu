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
.. module:: utils
   :platform: Unix
   :synopsis: Simple data utility methods
.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import copy

# A dictionary of available patterns (and ranks, needed for dawn)
pattern_list = {"SINOGRAM": 2,
                "PROJECTION": 2,
                "VOLUME_YZ": 2,
                "VOLUME_XZ": 2,
                "VOLUME_XY": 2,
                "VOLUME_3D": 3,
                "SPECTRUM": 1,
                "DIFFRACTION": 2,
                "CHANNEL": 1,
                "SPECTRUM_STACK": 2,
                "PROJECTION_STACK": 3,
                "METADATA": 0,
                "4D_SCAN": 3,
                "TIMESERIES": 1,
                "MOTOR_POSITION": 2,
                "TANGENTOGRAM": 2,
                "SINOMOVIE": 3,
                "SINOGRAM_STACK": 3}


def _deepcopy_data_object(dObj, new_obj):
    """ Deepcopy data object, associating hdf5 objects that can not be copied.
    """
    new_obj.meta_data = dObj.meta_data
    new_obj.pattern_list = copy.deepcopy(dObj.pattern_list)
    new_obj.data_info = copy.deepcopy(dObj.data_info)
    new_obj.exp = dObj.exp
    new_obj._plugin_data_obj = dObj._plugin_data_obj
    new_obj.dtype = copy.deepcopy(dObj.dtype)
    new_obj.remove = copy.deepcopy(dObj.remove)
    new_obj.group_name = dObj.group_name
    new_obj.group = dObj.group
    new_obj.backing_file = dObj.backing_file
    new_obj.data = dObj.data
    new_obj.next_shape = copy.deepcopy(dObj.next_shape)
    new_obj.orig_shape = copy.deepcopy(dObj.orig_shape)
    new_obj.previous_pattern = copy.deepcopy(dObj.previous_pattern)
    new_obj._set_transport_data(dObj.data_info.get('transport'))
    return new_obj


def get_available_pattern_types():
    return list(pattern_list.keys())


def get_pattern_rank(pattern):
    return pattern_list[pattern]
