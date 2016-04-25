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
from savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18fluo_loader import I18fluoLoader
from savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18xrd_loader import I18xrdLoader
from savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18stxm_loader import I18stxmLoader
from savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18monitor_loader import I18monitorLoader

import logging

from savu.plugins.utils import register_plugin


@register_plugin
class I18MmLoader(BaseLoader):
    """
    A class to load tomography data from an NXTomo file
    :param fast_axis: what is the fast axis called. Default:"x".
    :param scan_pattern: what was the scan. Default: ["rotation","x"].
    :param x: where is x in the \
        file. Default:'entry1/raster_counterTimer01/traj1ContiniousX'.
    :param y: where is y in the file. Default:None.
    :param rotation: where is rotation in the \
        file. Default:'entry1/raster_counterTimer01/sc_sample_thetafine'.
    :param monochromator: where is the \
        monochromator. Default: 'entry1/instrument/DCM/energy'.
    :param stxm_detector: path to stxm. Default:'entry1/raster_counterTimer01/It'.
    :param monitor_detector: path to stxm. Default:'entry1/raster_counterTimer01/I0'.
    :param fluo_detector: path to stxm. Default:'entry1/xspress3/AllElementSum'.
    :param data_path: Path to the folder containing the \
        data. Default: 'Savu/test_data/data/image_test/tiffs'.
    :param calibration_path: path to the calibration file. Default: "Savu/test_data/data/LaB6_calibration_output.nxs".
    
    """

    def __init__(self, name='I18MmLoader'):
        super(I18MmLoader, self).__init__(name)

    def setup(self):
#         new_dict = self.amend_dictionary()
        
#         try:
#             self.setup_loader(I18fluoLoader(), self.parameters.copy())
#             logging.debug('This file contains an fluo')
#         except:
#             logging.warn('This file does not contain an fluo')
        try:
            self.setup_loader(I18xrdLoader(), self.parameters.copy())
            logging.debug('This file contains an xrd')
        except:
            logging.warn('This file does not contain an xrd')
        try:
            self.setup_loader(I18stxmLoader(), self.parameters.copy())
            logging.debug('This file contains an stxm')
        except:
            logging.warn('This file does not contain an stxm')

        try:
            self.setup_loader(I18monitorLoader(), self.parameters.copy())
            logging.debug('This file contains a monitor')
        except:
            logging.warn('This file does not contain an monitor')

    def setup_loader(self, loader, params):
        logging.debug('I am here')
        loader._main_setup(self.exp, params)
        logging.debug('now I am here')
#         logging.debug('Have done the main setup on %s' % loader.__name__)
        loader.setup()

    def amend_dictionary(self):
        new_dict = self.parameters.copy()
        del new_dict['calibration_path']
        return new_dict
