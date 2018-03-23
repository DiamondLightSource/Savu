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
.. module:: yaml_loader
   :platform: Unix
   :synopsis: A class to load data from a non-standard nexus/hdf5 file using \
   descriptions loaded from a yaml file.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import h5py

from savu.plugins.utils import register_plugin
from savu.plugins.loaders.yaml_converter import YamlConverter


@register_plugin
class Hdf5TemplateLoader(YamlConverter):
    """
    A class to load data from a non-standard nexus/hdf5 file using \
    descriptions loaded from a yaml file.

    :u*param yaml_file: Path to the file containing the data \
        descriptions. Default: None.
    """

    def __init__(self, name='Hdf5TemplateLoader'):
        super(Hdf5TemplateLoader, self).__init__(name)

    def set_data(self, dObj, data):
        path = data['path'] if 'path' in data.keys() else None
        if not path:
            emsg = 'Please specify the path to the data in the h5 file.'
            raise Exception(emsg)

        file_path = self.exp.meta_data.get("data_file") if 'file' not in \
            data.keys() else data['file']
        file_path = self.update_value(dObj, file_path)
        dObj.backing_file = h5py.File(file_path, 'r')
        dObj.data = dObj.backing_file[self.update_value(dObj, path)]
        dObj.set_shape(dObj.data.shape)
        return dObj
