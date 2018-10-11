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
.. module:: hilbert_filter
   :platform: Unix
   :synopsis: A plugin to apply hilbert filter horizontally for tomo reconstruction of phase gradient images. Use before Vocentering. In AstraRecon set log to false and FBP_filter to none.

.. moduleauthor:: Tunhe Zhou <tunhe.zhou@diamond.ac.uk>

"""
import logging
import numpy as np
import pyfftw.interfaces.scipy_fftpack as fft


from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class HilbertFilter(BaseFilter, CpuPlugin):
    """
    A plugin to apply Hilbert filter (for phase gradient image) on projections.

    """

    def __init__(self):
        """
        This is where the class is designed, and we inherit from 2 classes, the
        first is the Filter class, which deals with splitting the job up for
        us, and provides some simple methods which we need to overload. The
        second is the CpuPlugin class which tells the framework that the
        processing that you are doing here runs on 1 cpu.
        """
        logging.debug("initialising Hilbert filter")
        logging.debug("Calling super to make sure that all superclases are " +
                      " initialised")
        super(HilbertFilter, self).__init__('HilbertFilter')
        self.filter1 = None

    def pre_process(self):
        self._setup_hilbert(*self.get_plugin_in_datasets()[0].get_shape())

    def _setup_hilbert(self, height, width):
        centerx = np.ceil(width / 2.0)
        # Define the hilbert filter
        filter1 = np.ones((height, width), dtype=np.float32)
        filter1[:,0:int(centerx)] = filter1[:,0:int(centerx)]*(-1.0)
        self.filter1 = filter1

    def _hilbert(self, data):
        pci1 = fft.fft2(fft.fftshift(np.float32(data)))
        pci2 = fft.ifftshift(pci1)*self.filter1
        fpci0 = fft.ifftshift(fft.ifft2(fft.fftshift(pci2)))
        fpci = np.imag(fpci0)
        result = fpci
        return result

    def process_frames(self, data):
        proj = np.nan_to_num(data[0])
        return self._hilbert(proj)

    def get_max_frames(self):
        return 'single'

