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


def set_preview_note():
    """
        Each ``preview_list`` element should be of the form
        ``start:stop:step:chunk``, where ``step`` and ``chunk`` are optional
        (default = 1) but both are required if chunk > 1.

        .. note::
            **start:stop[:step]**
                represents the set of indices specified by:

                >>> indices = range(start, stop[, step])
            For more information see :func:`range`

            **start:stop:step:chunk (chunk > 1)**
                represents the set of indices specified by:

                >>> a = np.tile(np.arange(starts[dim], stops[dim], \
steps[dim]), (chunk, 1))
                >>> b = np.transpose(np.tile(np.arange(chunk)-chunk/2, \
(a.shape[1], 1)))
                >>> indices = np.ravel(np.transpose(a + b))

                Chunk indicates how many values to take around each value in
                ``range(start, stop, step)``.

                .. warning:: If any indices are out of range (or negative)
                    then the list is invalid. When chunk > 1, new start and
                    end values will be:

                    >>> new_start = start - int(chunk/2)
                    >>> new_end = range(start, stop, step)[-1] + \
(step - int(chunk/2))

        **accepted values**:
            All values should be positive integers or one of the following
            keywords:

            * ``:`` is a simplification for 0:end:1:1 (all values)
            * ``mid`` is int(shape[dim]/2)
            * ``end`` is shape[dim]
            * ``midmap`` is the ``mid`` of a mapped dimension (only relevant \
in a 'dimension mapping' loader)
    """
    pass
