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
.. module:: tomophantom_loader
   :platform: Unix
   :synopsis: A full-field tomography loader that creates a NeXus file in \
   NXtomo format and contains tomographic synthetic data generated hdf5 dataset of a \
   specified size.

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.plugins.utils import register_plugin
from savu.plugins.loaders.base_tomophantom_loader import BaseTomophantomLoader
from savu.data.data_structures.data_types.data_plus_darks_and_flats \
    import ImageKey


@register_plugin
class TomoPhantomLoader(BaseTomophantomLoader):
    def __init__(self, name='TomoPhantomLoader'):
        super(TomoPhantomLoader, self).__init__(name)

    def setup(self):
        data_obj,data_obj2 = super(TomoPhantomLoader, self).setup()

        image_key = self.__set_image_key(data_obj)
        data_obj.data = ImageKey(data_obj, image_key, 0)
        data_obj.set_shape(data_obj.data.shape)
        self.set_data_reduction_params(data_obj)

        data_obj2.set_shape(data_obj2.data.shape)
        self.set_data_reduction_params(data_obj2)

        super(TomoPhantomLoader, self).post_process(data_obj, data_obj2)

    def __set_image_key(self, data_obj):
        proj_slice = \
            data_obj.get_data_patterns()['PROJECTION']['slice_dims'][0]
        image_key = np.zeros(data_obj.data.shape[proj_slice], dtype=int)
        return image_key
