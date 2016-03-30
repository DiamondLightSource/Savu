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
import savu.core.utils as cu


pattern_list = ["SINOGRAM",
                "PROJECTION",
                "VOLUME_YZ",
                "VOLUME_XZ",
                "VOLUME_XY",
                "VOLUME_3D",
                "SPECTRUM",
                "DIFFRACTION",
                "CHANNEL",
                "SPECTRUM_STACK",
                "PROJECTION_STACK",
                "METADATA"]


def _deepcopy_data_object(dObj, new_obj):
    """ Deepcopy data object, associating hdf5 objects that can not be copied.
    """
    cu.add_base_classes(new_obj, dObj._get_transport_data())
    new_obj.meta_data = dObj.meta_data
    new_obj.pattern_list = copy.deepcopy(dObj.pattern_list)
    new_obj.data_info = copy.deepcopy(dObj.data_info)
    new_obj.exp = dObj.exp
    new_obj._plugin_data_obj = dObj._plugin_data_obj
    new_obj.tomo_raw_obj = dObj.tomo_raw_obj
    new_obj.data_mapping = dObj.data_mapping
    new_obj.dtype = copy.deepcopy(dObj.dtype)
    new_obj.remove = copy.deepcopy(dObj.remove)
    new_obj.group_name = dObj.group_name
    new_obj.group = dObj.group
    new_obj.backing_file = dObj.backing_file
    new_obj.data = dObj.data
    new_obj.next_shape = copy.deepcopy(dObj.next_shape)
    new_obj.mapping = copy.deepcopy(dObj.mapping)
    new_obj.map_dim = copy.deepcopy(dObj.map_dim)
    new_obj.revert_shape = copy.deepcopy(dObj.map_dim)
    return new_obj


def get_available_pattern_types():
    return pattern_list
