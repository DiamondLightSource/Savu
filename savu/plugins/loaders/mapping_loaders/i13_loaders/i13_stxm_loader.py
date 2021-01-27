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
.. module:: i13_stxm_loader
   :platform: Unix
   :synopsis: A class for loading nxstxm data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
import h5py


@register_plugin
class I13StxmLoader(BaseLoader):
    """
    A class to load tomography data from the txm
    """

    def __init__(self, name='I13StxmLoader'):
        super(I13StxmLoader, self).__init__(name)

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

        data_obj.data = data_obj.backing_file['/entry1/merlin_sw_hdf/merlin_tot']
        sh = data_obj.data.shape
        #print sh
        ### set the rotation
        rotation_angle = \
            data_obj.backing_file['entry1/merlin_sw_hdf/t1_theta'][()].astype(float)[:,0]
        #print rotation_angle.shape
        data_obj.meta_data.set('rotation_angle', rotation_angle)
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'x.pixel')

        data_obj.add_pattern('PROJECTION', core_dims=(1,),slice_dims=(0,))
        data_obj.add_pattern('SINOGRAM', core_dims=(0,1),slice_dims=())
#         data_obj.add_pattern('PROJECTION', core_dir=(0,), slice_dir=(1,2,3))
#         data_obj.add_pattern('SPECTRUM', core_dir=(3,), slice_dir=(0,1,2))

        data_obj.set_shape(sh)
        self.set_data_reduction_params(data_obj)
