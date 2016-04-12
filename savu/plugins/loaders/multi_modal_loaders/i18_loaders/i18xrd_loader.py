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
.. module:: I18stxm_loader
   :platform: Unix
   :synopsis: A class for loading I18's stxm data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.multi_modal_loaders.base_i18_multi_modal_loader import BaseI18MultiModalLoader

from savu.plugins.utils import register_plugin
import h5py
import tempfile

@register_plugin
class I18xrdLoader(BaseI18MultiModalLoader):
    """
    A class to load tomography data from an NXstxm file
    :param data_path: Path to the folder containing the \
        data. Default: '../../../test_data/data/image_test/tiffs'.
    :param image_type: Type of image. Choose from 'FabIO'. Default: 'FabIO'.
    :param frame_dim: Which dimension requires stitching? Default: 0.
    """

    def __init__(self, name='I18xrdLoader'):
        super(I18xrdLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        
        data_obj = self.multi_modal_setup('xrd')
        dtype = self.parameters['image_type']
        mod = __import__('savu.data.data_structures.data_type', fromlist=dtype)
        clazz = getattr(mod, dtype)

        path = self.parameters['data_path']
        data_obj.data = clazz(path, data_obj, self.parameters['frame_dim'])
        # dummy file
        filename = path.split('/')[-1] + '.h5'
        data_obj.backing_file = \
            h5py.File(tempfile.mkdtemp() + '/' + filename, 'a')

        data_obj.set_shape(data_obj.data.get_shape())

        self.set_motors(data_obj, 'xrd')
        self.add_patterns_based_on_acquisition(data_obj, 'xrd')
        self.set_data_reduction_params(data_obj)
