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
.. module:: hdf5_tomo_saver
   :platform: Unix
   :synopsis: A class for saving tomography data using the standard savers
   library.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.core.utils import logmethod
from savu.plugins.base_saver import BaseSaver
import savu.data.transport_data.standard_savers as sSaver

class Hdf5TomoSaver(BaseSaver):
    """
    A class to save tomography data to a hdf5 file
    """
            
    def __init__(self, name='Hdf5TomoSaver'):
        super(Hdf5TomoSaver, self).__init__(name)
        
        
    @logmethod
    def setup(self, experiment):
        saver = sSaver.TomographySavers(experiment)
        return saver.save_to_hdf5(experiment)
