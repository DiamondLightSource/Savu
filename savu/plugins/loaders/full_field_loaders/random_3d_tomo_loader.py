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
   :synopsis: A full-field tomography loader that creates a NeXus file in \
   NXtomo format and contains a random number generated hdf5 dataset of a \
   specified size.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.loaders.random_hdf5_loader import RandomHdf5Loader
from savu.data.data_structures.data_types.data_plus_darks_and_flats \
    import ImageKey


@register_plugin
class Random3dTomoLoader(RandomHdf5Loader):
    """
    A hdf5 dataset of a specified size is created at runtime using numpy\
    random sampling (numpy.random), saved with relevant meta_data to a NeXus \
    file, and used as input. It recreates the behaviour of the nxtomo loader \
    but with random data.  The input file path passed to Savu will be ignored \
    (use a dummy).
    Note: Further extensions planned to allow the generated data to be \
    re-loaded with the nxtomo_loader.

    :param axis_labels: A list of axis labels. Default: ['rotation_angle.degrees', 'detector_y.angles', 'detector_x.angles'].
    :*param patterns: Patterns. Default: ['SINOGRAM.0c.1s.2c', 'PROJECTION.0s.1c.2c'].
    :*param dataset_name: The name assigned to the dataset. Default: 'tomo'.
    :u*param image_key: Specify position of darks and flats (in that order) \
    in the data. Default: [[0, 1], [2, 3]]
    """

    def __init__(self, name='Random3dTomoLoader'):
        super(Random3dTomoLoader, self).__init__(name)

    def setup(self):
        data_obj = super(Random3dTomoLoader, self).setup()
        image_key = self.__set_image_key(data_obj)
        data_obj.data = ImageKey(data_obj, image_key, 0)
        data_obj.set_shape(data_obj.data.shape)
        self.set_data_reduction_params(data_obj)
        data_obj.data._set_dark_and_flat()
        data_obj.data.update_dark(np.zeros(data_obj.data.dark().shape))
        data_obj.data.update_flat(np.ones(data_obj.data.flat().shape))

    def __set_image_key(self, data_obj):
        proj_slice = data_obj.get_data_patterns()['PROJECTION']['slice_dir'][0]
        image_key = np.zeros(data_obj.data.shape[proj_slice], dtype=int)
        dark, flat = self.parameters['image_key']
        image_key[np.array(dark)] = 2
        image_key[np.array(flat)] = 1
        return image_key

    def _set_rotation_angles(self, data_obj, nEntries):
        dark, flat = self.parameters['image_key']
        nEntries = nEntries - len(dark + flat)
        super(Random3dTomoLoader, self)._set_rotation_angles(
                data_obj, nEntries)
