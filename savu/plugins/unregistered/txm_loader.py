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
.. module:: txm_loader
   :platform: Unix
   :synopsis: A class for loading nxstxm data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_loader import BaseLoader
import numpy as np
from savu.plugins.utils import register_plugin
import logging
import h5py

#@register_plugin
class TxmLoader(BaseLoader):
    def __init__(self, name='TxmLoader'):
        super(TxmLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """

        exp = self.exp
        data_obj = exp.create_data_object('in_data', 'tomo')

        data_obj.backing_file = \
            h5py.File(self.exp.meta_data.get("data_file"), 'r')

        data_obj.data = data_obj.backing_file['/entry1/data']
        sh = data_obj.data.shape
        #print sh
        ### set the rotation
        rotation_angle = \
            data_obj.backing_file['entry1/theta'][()].astype(float)
        #print rotation_angle.shape
        data_obj.meta_data.set('rotation_angle', rotation_angle)
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'detector_y.pixel',
                                 'detector_x.pixel')

        data_obj.add_pattern('PROJECTION', core_dims=(1, 2),
                             slice_dims=(0,))
        data_obj.add_pattern('SINOGRAM', core_dims=(0, 2),
                             slice_dims=(1,))

        data_obj.set_shape(sh)
        self.set_data_reduction_params(data_obj)

        #print data_obj.get_data_patterns()
