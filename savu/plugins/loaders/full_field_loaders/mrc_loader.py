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

from savu.plugins.loaders.base_loader import BaseLoader
from savu.plugins.utils import register_plugin
from savu.data.data_structures.data_types.mrc import MRC as MrcType


@register_plugin
class MrcLoader(BaseLoader):
    """
    Load Medical Research Council (MRC) formatted image data.

    """

    def __init__(self, name='MrcLoader'):
        super(MrcLoader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', 'tomo')

        filename = exp.meta_data.get("data_file")
        data_obj.data = MrcType(data_obj, filename)

        # dummy file
        path = exp.meta_data.get("data_file")
        filename = path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        nDims = len(data_obj.data.get_shape())
        if nDims is 3:
            # change this
            rot = 2
            detY = 1
            detX = 0
            data_obj.set_axis_labels('rotation_angle.degrees',
                                     'detector_y.pixel',
                                     'detector_x.pixel')

            data_obj.add_pattern('PROJECTION', core_dir=(detX, detY),
                                 slice_dir=(rot,))
            data_obj.add_pattern('SINOGRAM', core_dir=(detX, rot),
                                 slice_dir=(detY,))
        elif nDims is 4:
            # 4D patterns need to be set here
            pass
        else:
            raise Exception('Incorrect number of data dimensions found in '
                            'mrc loader')

        data_obj.set_shape(data_obj.data.get_shape())
        self.set_data_reduction_params(data_obj)
