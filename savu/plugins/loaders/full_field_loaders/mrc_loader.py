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
.. module:: mrc_loader
   :platform: Unix
   :synopsis: A class for MRC data.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import tempfile
import numpy as np

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
from savu.data.data_structures.data_types.mrc import MRC as MrcType


@register_plugin
class MrcLoader(BaseLoader):
    """
    Load Medical Research Council (MRC) formatted image data.
    :param angles: A python statement to be evaluated \
    (e.g np.linspace(0, 180, nAngles)) or a file. Default: None.
    :param name: The name assigned to the dataset. Default: 'tomo'.

    """

    def __init__(self, name='MrcLoader'):
        super(MrcLoader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', self.parameters['name'])

        filename = exp.meta_data.get("data_file")
        data_obj.data = MrcType(data_obj, filename)

        # dummy file
        path = exp.meta_data.get("data_file")
        filename = path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        self._set_rotation_angles(data_obj)

        nDims = len(data_obj.data.get_shape())
        if nDims is 3:
            rot = 0
            detY = 1
            detX = 2
            data_obj.set_axis_labels('rotation_angle.degrees',
                                     'detector_y.pixel',
                                     'detector_x.pixel')

            data_obj.add_pattern('PROJECTION', core_dims=(detX, detY),
                                 slice_dims=(rot,))
            data_obj.add_pattern('SINOGRAM', core_dims=(detX, rot),
                                 slice_dims=(detY,))
        elif nDims is 4:
            # 4D patterns need to be set here
            pass
        else:
            raise Exception('Incorrect number of data dimensions found in '
                            'mrc loader')

        data_obj.set_shape(data_obj.data.get_shape())
        return data_obj

    def _set_rotation_angles(self, data_obj):
        angles = self.parameters['angles']

        if angles is None:
            angles = np.linspace(0, 180, data_obj.data.get_shape()[0])
        else:
            try:
                angles = eval(angles)
            except:
                try:
                    angles = np.loadtxt(angles)
                except:
                    raise Exception('Cannot set angles in loader.')

        n_angles = len(angles)
        data_angles = data_obj.data.get_shape()[0]
        if data_angles != n_angles:
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s", n_angles, data_angles)
        data_obj.meta_data.set("rotation_angle", angles)

