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
.. module:: temp_loader
   :platform: Unix
   :synopsis: A class for loading standard tomography data in a variety of
    formats.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py
import tempfile
import numpy as np

from savu.plugins.base_loader import BaseLoader
from savu.plugins.utils import register_plugin


@register_plugin
class ImageLoader(BaseLoader):
    """
    A class to load tomography data from a Nexus file
    :param data_path: Path to the folder containing the \
        data. Default: '../../../test_data/data/image_test/tiffs'.
    :param image_type: Type of image. Choose from 'FabIO'. Default: 'FabIO'.
    :param angles: list[first_angle, final_angle, angular_step] or \
        file. Default: None.
    :param frame_dim: Which dimension requires stitching? Default: 0.
    """

    def __init__(self, name='ImageLoader'):
        super(ImageLoader, self).__init__(name)

    def setup(self):
        exp = self.exp
        data_obj = exp.create_data_object('in_data', 'tomo')

        rot = 0
        detY = 1
        detX = 2
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'detector_y.pixel',
                                 'detector_x.pixel')

        data_obj.add_pattern('PROJECTION', core_dir=(detX, detY),
                             slice_dir=(rot,))
        data_obj.add_pattern('SINOGRAM', core_dir=(detX, rot),
                             slice_dir=(detY,))

        dtype = self.parameters['image_type']
        mod = __import__('savu.data.data_structures.data_type', fromlist=dtype)
        clazz = getattr(mod, dtype)

        path = self.parameters['data_path']
        data_obj.data = clazz(path, data_obj, self.parameters['frame_dim'])

        self.set_rotation_angles(data_obj)

        # dummy file
        filename = path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        data_obj.set_shape(data_obj.data.get_shape())
        self.set_data_reduction_params(data_obj)

    def set_rotation_angles(self, data_obj):
        angles = self.parameters['angles']
        if isinstance(angles, list):
            #*** use linspace for default and allow eval on input parameter"
            angles = np.arange(angles[0], angles[1]+angles[2], angles[2])
        else:
            try:
                angles = np.loadtxt(angles)
            except:
                raise Exception('Unable to open angles file.')

        n_angles = len(angles)
        data_angles = data_obj.data.get_shape()[0]
        if data_angles is not n_angles:
            raise Exception("The number of angles %s does not match the data "
                            "dimension length %s", n_angles, data_angles)
        data_obj.meta_data.set_meta_data("rotation_angle", angles)
