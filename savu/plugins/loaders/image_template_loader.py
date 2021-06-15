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
.. module:: image_template_loader
   :platform: Unix
   :synopsis: 'A class to load data from a folder of Fabio compatible images \
        using data descriptions loaded from a yaml file.'

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py

from savu.data.data_structures.data_types.image_data import ImageData
from savu.plugins.utils import register_plugin
from savu.plugins.loaders.yaml_converter import YamlConverter


@register_plugin
class ImageTemplateLoader(YamlConverter):
    def __init__(self, name='ImageTemplateLoader'):
        super(ImageTemplateLoader, self).__init__(name)

    def set_data(self, dObj, data):
        folder = data['folder'] if 'folder' in list(data.keys()) else None
        shape = data['shape'] if 'shape' in list(data.keys()) else None

        if not folder:
            raise Exception('Please specify the path to the folder of images.')
        if not shape:
            raise Exception('Please specify the final shape of the data.')

        folder = self.update_value(dObj, folder)
        file_path = self.exp.meta_data.get("data_file")
        dObj.backing_file = h5py.File(file_path, 'r')
        shape = tuple(self.update_value(dObj, shape))
        dObj.data = ImageData(folder, dObj, list(range(len(shape))), shape=shape)
        dObj.set_shape(dObj.data.get_shape())
        return dObj
