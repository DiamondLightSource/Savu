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
.. module:: i18_fluo_loader
   :platform: Unix
   :synopsis: A class for loading I18's stxm data

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.unregistered.i18_loaders.base_i18_multi_modal_loader\
    import BaseI18MultiModalLoader
import numpy as np
from savu.plugins.utils import register_plugin


class I18FluoLoader(BaseI18MultiModalLoader):
    def __init__(self, name='I18FluoLoader'):
        super(I18FluoLoader, self).__init__(name)

    def setup(self):
        data_str = self.parameters['fluo_detector']
        data_obj = self.multi_modal_setup('fluo', self.parameters['name'])
        data_obj.data = data_obj.backing_file[data_str]
        data_obj.set_shape(data_obj.data.shape)
        npts = data_obj.get_shape()[-1]
        mData = data_obj.meta_data
        mData.set("energy", np.arange(npts)*0.01)
        self.set_motors(data_obj, 'fluo')
        self.add_patterns_based_on_acquisition(data_obj, 'fluo')
        self.set_data_reduction_params(data_obj)
