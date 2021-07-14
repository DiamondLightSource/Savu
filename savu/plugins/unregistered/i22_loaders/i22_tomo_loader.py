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
.. module:: i22_tomo_loader
   :platform: Unix
   :synopsis: A class for loading I22

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.utils import register_plugin
from savu.plugins.loaders.base_loader import BaseLoader
import h5py
import logging
import numpy as np


#@register_plugin
class I22TomoLoader(BaseLoader):
    def __init__(self, name='I22TomoLoader'):
        super(I22TomoLoader, self).__init__(name)

    def setup(self):
        """
        """
        exp = self.exp
        data_obj = exp.create_data_object('in_data', 'tomo')
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get("data_file"), 'r')
        data_obj.data = data_obj.backing_file['entry/result/data']
        data_obj.set_shape(data_obj.data.shape)
        logging.warning('the data as shape %s' % str(data_obj.data.shape))
        data_obj.set_axis_labels('y.units', 'x.units',
                                 'rotation_angle.degrees', 'Q.angstrom^-1')

        data_obj.add_pattern('PROJECTION', core_dims=(1, 0), slice_dims=(2, 3))
        data_obj.add_pattern('SINOGRAM', core_dims=(2, 1), slice_dims=(0, 3))
        data_obj.add_pattern('SPECTRUM', core_dims=(3,), slice_dims=(0, 1, 2))

        mData = data_obj.meta_data
        mData.set("Q", data_obj.backing_file['entry/result/q'][()])
        mData.set("x", np.arange(data_obj.data.shape[1]))
        mData.set("y", np.arange(data_obj.data.shape[0]))
        mData.set("rotation_angle", data_obj.backing_file[
            'entry/result/theta'][()])

        self.set_data_reduction_params(data_obj)
