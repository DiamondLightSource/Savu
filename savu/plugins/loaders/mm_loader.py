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
.. module:: mm_loader
   :platform: Unix
   :synopsis: A class for loading multi-modal data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.core.utils import logmethod
from savu.plugins.base_loader import BaseLoader
from savu.plugins.loaders.multi_modal_loaders.nxfluo_loader import NxfluoLoader
from savu.plugins.loaders.multi_modal_loaders.nxxrd_loader import NxxrdLoader
from savu.plugins.loaders.multi_modal_loaders.nxstxm_loader import NxstxmLoader
from savu.plugins.loaders.multi_modal_loaders.nxmonitor_loader \
    import NxmonitorLoader

from savu.plugins.utils import register_plugin


@register_plugin
class MmLoader(BaseLoader):
    """
    A class to load tomography data from an NXTomo file

    :param calibration_path: path to the calibration file. Default: "Savu/test_data/data/LaB6_calibration_output.nxs".
    """

    def __init__(self, name='MmLoader'):
        super(MmLoader, self).__init__(name)

    def setup(self):
        new_dict = self.amend_dictionary()
        self.setup_loader(NxfluoLoader(), new_dict)
        self.setup_loader(NxxrdLoader(), self.parameters)
        self.setup_loader(NxstxmLoader(), new_dict)
        self.setup_loader(NxmonitorLoader(), new_dict)

    def setup_loader(self, loader, params):
        loader.main_setup(self.exp, params)
        loader.setup()

    def amend_dictionary(self):
        new_dict = self.parameters.copy()
        del new_dict['calibration_path']
        return new_dict
