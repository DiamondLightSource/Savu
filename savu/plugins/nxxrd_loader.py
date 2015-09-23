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

from savu.core.utils import logmethod
from savu.plugins.base_loader import BaseLoader
import savu.data.transport_data.standard_loaders as sLoader

from savu.plugins.utils import register_plugin


@register_plugin
class NxxrdLoader(BaseLoader):
    """
    A class to load tomography data from an NXxrd file
        
    :param calibration_path: path to the calibration file. Default: "../../test_data/LaB6_calibration_output.nxs"

    """
            
    def __init__(self, name='NxxrdLoader'):
        super(NxxrdLoader, self).__init__(name)
        
        
    @logmethod
    def setup(self, experiment):
        loader = sLoader.XRDLoaders(self.parameters)
        loader.load_from_nx_xrd(experiment)
        
