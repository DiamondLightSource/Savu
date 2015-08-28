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
.. module:: tomography_loader
   :platform: Unix
   :synopsis: A class for loading tomography data using the standard loaders 
   library.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

# The following is the start of a really dirty hack to get a multimodal dataset in. This is not how it should be done, but is just to get things moving for now.
#It will be replaced when the code is refactored. Aaron.
# PS. Sorry Mark and Nic for making the pretty thing ugly....
from savu.core.utils import logmethod
from savu.plugins.base_loader import BaseLoader
import savu.data.transport_data.standard_loaders as sLoader

from savu.plugins.utils import register_plugin


@register_plugin
class MmLoader(BaseLoader):
    """
    A class to load tomography data from an NXTomo file
    :param calibration_path: path to the calibration file. Default: "../test_data/LaB6_calibration_output.nxs"
    """
            
    def __init__(self, name='MmLoader'):
        super(MmLoader, self).__init__(name)
        
        
    @logmethod
    def setup(self, experiment):
        loader1 = sLoader.FluorescenceLoaders(experiment)
        loader1.load_from_nx_fluo(experiment)
        loader2 = sLoader.XRDLoaders(experiment, self.parameters)
        loader2.load_from_nx_xrd(experiment)
        loader3 = sLoader.STXMLoaders(experiment)
        loader3.load_from_nx_stxm(experiment)