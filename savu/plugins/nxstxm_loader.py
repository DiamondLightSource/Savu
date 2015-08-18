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

class NxstxmLoader(BaseLoader):
    """
    A class to load tomography data from an NXFluo file
    """
            
    def __init__(self, name='NxstxmLoader'):
        super(NxstxmLoader, self).__init__(name)
        
        
    @logmethod
    def setup(self, experiment):
        loader = sLoader.STXMLoaders(experiment)
        loader.load_from_nx_stxm(experiment)
        
