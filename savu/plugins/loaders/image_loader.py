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

from savu.plugins.base_loader import BaseLoader
from savu.data.data_structures.data_type import DataTiff

from savu.plugins.utils import register_plugin


@register_plugin
class ImageLoader(BaseLoader):
    """
    A class to load tomography data from a Nexus file
    :param data_path: Path to the folder containing the \
        data. Default: '../../../test_data/data/image_test'.
    :param file_name: Name of the first file. Default: "".
    :param image_type: Type of image. Default: "DataTiff".
    :param data_shape: A tuple of data dimensions. Default: ().
    :param frame_dim: Frame dimension. Default: 0.
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

        data_obj.data = DataTiff(self.parameters['data_path'], data_obj,
                                 self.parameters['frame_dim'],
                                 self.parameters['file_name'])
        # dummy file
        data_obj.backing_file = h5py.File("/dls/tmp/qmm55171/temp.h5", "w")

        data_obj.set_shape(tuple(self.parameters['data_shape']))
        self.set_data_reduction_params(data_obj)
