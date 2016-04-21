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
import numpy as np
from savu.plugins.utils import register_plugin


@register_plugin
class I18fluoLoader(BaseI18MultiModalLoader):
    """
    A class to load tomography data from an NXstxm file
    :param fluo_detector: path to stxm. Default:'entry1/xspress3/AllElementSum'.
    :param fluo_offset: fluo scale offset. Default: 0.0.
    :param fluo_gain: fluo gain. Default: 0.01.

    """

    def __init__(self, name='I18fluoLoader'):
        super(I18fluoLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file
        :param path: The full path of the NeXus file to load.
        :type path: str
        """
        
        data_str = self.parameters['fluo_detector']
        data_obj = self.multi_modal_setup('fluo')
        data_obj.data = data_obj.backing_file[data_str]
        data_obj.set_shape(data_obj.data.shape)
        npts = data_obj.get_shape()[-1]
        mData = data_obj.meta_data
        gain = self.parameters["fluo_gain"]
        energy = np.arange(self.parameters["fluo_offset"], gain*npts, gain)
        mData.set_meta_data("energy", energy)
        self.set_motors(data_obj, 'fluo')
        self.add_patterns_based_on_acquisition(data_obj, 'fluo')
        self.set_data_reduction_params(data_obj)
